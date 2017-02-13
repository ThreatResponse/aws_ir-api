#!/usr/bin/python

import pytest
import boto3
import base64
import os
import json
import requests
import time
import uuid

from faker import Factory
from dotenv import Dotenv
# from api import app as api

CFN_TEMPLATE_PATH = "cfn/dummy-machine.yml"
SESSION = boto3.Session(
        profile_name='incident-account',
        region_name='us-west-2'
    )
EC2_CLIENT = SESSION.client('ec2')
CFN_CLIENT = SESSION.client('cloudformation')

STACKNAME="InstanceCompromise-{stack_uuid}".format(stack_uuid=uuid.uuid4().hex)
FAKE_SORT_KEY="000account000+awsir-api-test-user"

compromised_resource = {}

def setup_module(module):
    print ("setup_module:%s" % module.__name__)
    create_stack()
    module.compromised_resource = find_host()
    create_credential()


def teardown_module(module):
    print ("teardown_module:%s" % module.__name__)
    CFN_CLIENT.delete_stack(StackName=STACKNAME)
    destroy_credential()

def create_credential():
    """Write our fake test cred to dynamo"""
    credential = get_credential()
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('dev_credential')
    response = table.put_item(
        Item={
                'credential_id': FAKE_SORT_KEY,
                'read_credential': credential,
                'write_credential': credential
            }
    )
    pass

def get_credential():
    """Get a temporary token for this user to store in Dyanmo for retrieval"""
    client = boto3.client('sts')

    #Generate a very short lived token to store in dynamo
    response = client.get_session_token(
        DurationSeconds=900
    )['Credentials']

    response['Expiration'] = response['Expiration'].isoformat()
    urlsafe_response = json.dumps(response)
    response = base64.b64encode(urlsafe_response).encode('utf-8')
    return response

def destroy_credential():
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('dev_credential')
    response = table.delete_item(
        Key={
            'credential_id': FAKE_SORT_KEY
        }
    )

def create_stack():
    with open(CFN_TEMPLATE_PATH) as f:
        CFN_CLIENT.create_stack(
            StackName = STACKNAME,
            TemplateBody = f.read(),
            Capabilities = ['CAPABILITY_IAM']
        )

def find_host():
    host_public_ip = find_host_ip()
    response = EC2_CLIENT.describe_instances(
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
    for reservation in response['Reservations']:
        instance = reservation['Instances'][0]
        ip_address = instance.get('PublicIpAddress', None)
        if ip_address == host_public_ip:
            print("Instance Found")
            incident_instance = instance

    return {
        'vpc_id': incident_instance['VpcId'],
        'region': 'us-west-2',
        'case_number': '1234567',
        'instance_id':  incident_instance['InstanceId'],
        'compromise_type': 'host',
        'private_ip_address': incident_instance.get('PrivateIpAddress', None),
        'public_ip_address': incident_instance.get('PublicIpAddress', None),
    }

def find_host_ip():
    host_public_ip = None
    while host_public_ip == None:
        try:
            response = CFN_CLIENT.describe_stacks(
                StackName=STACKNAME
            )
            ip = response['Stacks'][0]['Outputs'][0]['OutputValue']
            print ip
            return ip

        except:
            time.sleep(10)
            continue

class AwsirApi(object):
    def __init__(self):
        self.url = 'http://localhost:8000'

    def get_json(self, url):
        if not url.startswith('/'):
            url = '/' + url
        response = requests.get(self.url + url)
        response.raise_for_status()
        return response.json()

    def post(self, plugin, host):
        host['sort_key'] = FAKE_SORT_KEY
        print("{} {}").format(plugin, host)
        endpoint = "/hosts/{}/{}".format(host.get('instance_id'), plugin)

        response = requests.post(self.url + endpoint, json=host)
        return response


def test_index():
    print("If this fails make sure Chalice local is running")
    assert AwsirApi().get_json('/') == {'AWS_IR-api': 'experimental'}


def test_isolate():
    response = AwsirApi().post('isolate_host', compromised_resource)
    assert response.json() == {'isolate_host': True}

def test_tag():
    response = AwsirApi().post('tag_host', compromised_resource)
    assert response.json() == {'tag_host': True}

def test_gather():
    response = AwsirApi().post('gather', compromised_resource)
    assert response.json() == {'gather': True}

