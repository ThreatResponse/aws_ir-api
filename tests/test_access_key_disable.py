#!/usr/bin/python

import pytest
import boto3
import base64
import os
import json

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

def setup_test():
    template = ""
    with open(CFN_TEMPLATE_PATH) as f:
        CLIENT.create_stack(
            StackName='InsecureDaveKeyTest',
            TemplateBody=f.read(),
            Capabilities=[
            'CAPABILITY_IAM'
            ]
        )


def teardown_test():
    CLIENT.delete_stack(
        StackName='InsecureDaveKeyTest'
    )
