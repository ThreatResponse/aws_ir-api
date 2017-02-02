#!/usr/bin/python

import pytest
import boto3
import base64
import os
import json
import time
import uuid
import socket

from faker import Factory
from dotenv import Dotenv
from api.chalicelib.aws_ir.aws_ir.plugins import tag_host



CFN_TEMPLATE_PATH = "cfn/dummy-machine.yml"
try:
    SESSION = boto3.Session(
        profile_name='incident-account',
        region_name='us-west-2'
    )

    CLIENT = SESSION.client('cloudformation')
except:
    raise


STACKNAME="InstanceCompromise-{stack_uuid}".format(stack_uuid=uuid.uuid4().hex)
INCIDENT_PUBLIC_IP=None

def incident_client():
    return SESSION.client('ec2')

def port_is_open(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip,port))
    if result == 0:
       return True
    else:
       return False

def instance_ready():
    try:
        response = CLIENT.describe_stacks(
            StackName=STACKNAME
        )
        instanceIP = response['Stacks'][0]['Outputs'][0]['OutputValue']
        INCIDENT_PUBLIC_IP = instanceIP
        return instanceIP
    except:
        time.sleep(10)
        return None


def setup_test():
    template = ""
    with open(CFN_TEMPLATE_PATH) as f:
        try:
            CLIENT.create_stack(
                StackName=STACKNAME,
                TemplateBody=f.read(),
                Capabilities=[
                'CAPABILITY_IAM'
                ]
            )
            while instance_ready() == None:
                pass
        except:
            while instance_ready() == None:
                pass

def test_incident_public_ip_exists():
    assert instance_ready() is not None


def test_plugin():
    client = incident_client()
    response = client.describe_instances(
            Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running',
                    'pending'
                ]
            },
        ],
    )
    incident_instance = None

    #Maybe can replace with list comprehension
    for instance in response['Reservations']:
        ip_address = instance.get('PublicIpAddress', None)
        if ip_address == INCIDENT_PUBLIC_IP:
            print("Instance Found")
            incident_instance = instance['Instances'][0]

    #Crafting this by hand to avoid complex interaction
    #AWS_IR inventory class needs a refactor.

    resource = {
        'vpc_id': incident_instance['VpcId'],
        'region': 'us-west-2',
        'case_number': '1234567',
        'instance_id':  incident_instance['InstanceId'],
        'compromise_type': 'host',
        'private_ip_address': incident_instance.get('PrivateIpAddress', None),
    }


    plugin = tag_host.Tag(
        client=client,
        compromised_resource=resource,
        dry_run=False

    )
    status = plugin.validate()
    assert status == True

def teardown_test():
    try:
        #Once I had to clean up a lot of failed stacks
        #I may move this to an hourly cloud custodian package.
        response = CLIENT.describe_stacks()
        for stack in response['Stacks']:
            if stack['StackName'].find('InstanceCompromise'):
                CLIENT.delete_stack(
                    StackName=response['Stacks'][0]['StackName']
                )

        CLIENT.delete_stack(
            StackName=STACKNAME
        )
        pass
    except:
        #There is probably no stack to delete
        pass
