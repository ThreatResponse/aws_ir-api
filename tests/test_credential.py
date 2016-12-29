#!/usr/bin/python

import pytest
import boto3
import base64
import os
import json

from faker import Factory
from dotenv import Dotenv
from api import credential

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError

def get_token():
    """Get a temporary token for this user to store in Dyanmo for retrieval"""
    client = boto3.client('sts')

    #Generate a very short lived token to store in dynamo
    response = client.get_session_token(
        DurationSeconds=900
    )['Credentials']

    response['Expiration'] = response['Expiration'].isoformat()

    response = base64.urlsafe_b64encode(json.dumps(response))


    return response


def delete_token():
    """Remove token from dynamo table"""
    pass

def fake_sort_key():
    """Generate a fake sort-key in the form of user-email+account_id"""
    fake = Factory.create()

    account_id = "671642278147"
    email = fake.email()
    return "{account_id}+{email}".format(account_id=account_id, email=email)


def dynamo_write(sort_key, credential):
    """Write our fake test cred to dynamo"""
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('dev_credential')
    response = table.put_item(
        Item={
                'credential_id': sort_key,
                'read_credential': credential,
                'write_credential': credential

            }
    )
    pass


SORT_KEY = fake_sort_key()
def setup_test():
    CREDENTIAL = get_token()
    #print(CREDENTIAL)
    dynamo_write(SORT_KEY, CREDENTIAL)

    pass

def test_object_instiation():
    c = credential.Credential(SORT_KEY)
    print ("setting up %s" % SORT_KEY)
    assert c.sort_key is SORT_KEY



def teardown_tokens():
    pass
