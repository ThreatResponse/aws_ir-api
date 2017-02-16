#!/usr/bin/python

import pytest
import boto3
import base64
import os
import json
import time
import uuid

from faker import Factory
from dotenv import Dotenv
from api.chalicelib.aws_ir.aws_ir.plugins import tag_host



CFN_TEMPLATE_PATH = "cfn/dummy-machine.yml"
SESSION = boto3.Session(
    profile_name='incident-account',
    region_name='us-west-2'
)

CFN_CLIENT = SESSION.client('cloudformation')
EC2_CLIENT = SESSION.client('ec2')

STACKNAME="InstanceCompromise-{stack_uuid}".format(stack_uuid=uuid.uuid4().hex)

def setup_module(module):
    print ("setup_module:%s" % module.__name__)
    with open(CFN_TEMPLATE_PATH) as f:
        CFN_CLIENT.create_stack(
            StackName = STACKNAME,
            TemplateBody = f.read(),
            Capabilities = ['CAPABILITY_IAM']
        )

def teardown_module(module):
    print ("teardown_module:%s" % module.__name__)
    CFN_CLIENT.delete_stack(StackName=STACKNAME)

def find_host():
    host_instance_id = find_host_id()
    response = EC2_CLIENT.describe_instances(
            InstanceIds=[host_instance_id]
    )

    incident_instance = response['Reservations'][0]['Instances'][0]

    return {
        'vpc_id': incident_instance['VpcId'],
        'region': 'us-west-2',
        'case_number': '1234567',
        'instance_id':  incident_instance['InstanceId'],
        'compromise_type': 'host',
        'private_ip_address': incident_instance.get('PrivateIpAddress', None),
        'public_ip_address': incident_instance.get('PublicIpAddress', None),
    }

def find_host_id():
    host_instance_id = None
    retries = 0
    while host_instance_id == None and retries < 30:
        try:
            response = CFN_CLIENT.describe_stacks(
                StackName=STACKNAME
            )
            host_instance_id = response['Stacks'][0]['Outputs'][0]['OutputValue']
            print "found {}".format(host_instance_id)
            return host_instance_id

        except:
            ++retries
            time.sleep(10)
            continue

def test_plugin():
    resource = find_host()

    plugin = tag_host.Tag(
        client=EC2_CLIENT,
        compromised_resource=resource,
        dry_run=False

    )
    status = plugin.validate()
    assert status == True
