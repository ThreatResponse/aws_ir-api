#!/usr/bin/python

import pytest
import boto3
import base64
import os
import json
import time

from faker import Factory
from dotenv import Dotenv
from api.chalicelib.aws_ir.aws_ir.plugins import disableaccess_key


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

def get_access_key_id():
    try:
        response = CLIENT.describe_stacks(
            StackName='InsecureDaveKeyTest'

        )
        access_key_id = response['Stacks'][0]['Outputs'][0]['OutputValue']
    except:
        access_key_id = None
        time.sleep(2)
    return access_key_id

def incident_client():
    return SESSION.client('iam')

def setup_test():
    template = ""
    with open(CFN_TEMPLATE_PATH) as f:
        try:
            CLIENT.create_stack(
                StackName='InsecureDaveKeyTest',
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

def test_disable_access_key():
    assert INCIDENT_ACCESS_KEY_ID is not None
    compromised_resource = {
        'access_key_id': get_access_key_id(),
        'compromise_type': 'KeyCompromise'
    }

    client = incident_client()

    plugin = disableaccess_key.Disableaccess(
        client, compromised_resource, False
    )


    validation = plugin.validate()

    assert validation is True

def teardown_test():
    CLIENT.delete_stack(
        StackName='InsecureDaveKeyTest'
    )
