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
from api.chalicelib.aws_ir.aws_ir.plugins import revokests_key


CFN_TEMPLATE_PATH = "cfn/dummy-user.yml"
try:
    SESSION = boto3.Session(
        profile_name='incident-account',
        region_name='us-west-2'
    )

    CLIENT = SESSION.client('cloudformation')
except:
    raise


INCIDENT_ACCESS_KEY_ID = ""
STACKNAME="InsecureDaveKeyTest-{stack_uuid}".format(stack_uuid=uuid.uuid4().hex)

def get_access_key_id():
    try:
        response = CLIENT.describe_stacks(
            StackName=STACKNAME
        )
        access_key_id = response['Stacks'][0]['Outputs'][0]['OutputValue']
    except:
        access_key_id = None
        time.sleep(4)
    return access_key_id

def incident_client():
    return SESSION.client('iam')

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
            while get_access_key_id() == None:
                INCIDENT_ACCESS_KEY_ID = get_access_key_id()

        except:
            while get_access_key_id() == None:
                INCIDENT_ACCESS_KEY_ID = get_access_key_id()

            pass

def test_session_token_revocation():
    assert INCIDENT_ACCESS_KEY_ID is not None
    compromised_resource = {
        'access_key_id': get_access_key_id(),
        'compromise_type': 'KeyCompromise'
    }
    #Get a client in the context of our incident account
    client = incident_client()
    #Instantiate the plugin
    plugin = revokests_key.RevokeSTS(
        client, compromised_resource, False
    )
    #Validate the the key is actually disabled
    validation = plugin.validate()
    assert validation is True



def teardown_test():
    try:
        #Once I had to clean up a lot of failed stacks
        response = CLIENT.describe_stacks()
        for stack in response['Stacks']:
            if stack['StackName'].find('InsecureDaveKeyTest'):
                CLIENT.delete_stack(
                    StackName=response['Stacks'][0]['StackName']
                )

        CLIENT.delete_stack(
            StackName=STACKNAME
        )
    except:
        #There is probably no stack to delete
        pass
