#!/usr/bin/python
import os
import boto3
import base64
import json
import dateutil.parser
import datetime
import time
from dotenv import Dotenv

"""This class retreives credentials from Dyanmo in AWS for Incident Pony"""



class Credential(object):
    """Initialize a Dynamo Client as needed and retreive\
    and eventually decrypt the payload for use in API operations\
    Role assumption is known to have happened somewhere else
    """

    def __init__(self, sort_key):
        try:
            env = Dotenv('./.env')
            credential_table = env["CREDENTIAL_TABLE_ARN"]
        except IOError:
            try:
                env = Dotenv('../.env')
                credential_table = env["CREDENTIAL_TABLE_ARN"]
            except:
                 env = os.environ

        self.sort_key = sort_key
        self.table_name = credential_table.split('/')[1]
        self.dynamodb = None

    def check(self, operation):
        """Returns true or false against determination if \
        the credential is valid"""
        if operation == 'read':
            credential = self.read()
        elif operation == 'write':
            credential = self.write()

        #Test expiration if not expired try to use it
        if self.__is_expired(credential) == True:
            return False
        elif self.__can_get_caller(credential) == False:
            return False
        else:
            return True

    def read(self):
        """Returns the decrypted read credential from dyanmo database"""
        if self.dynamodb:
            pass
        else:
            self.__connect()

        try:
            item = self.table.get_item(
                Key={
                    'credential_id': self.sort_key
                }
            )['Item']


            read_credential = item['read_credential']
            item = json.loads(
                base64.b64decode(read_credential).decode('utf-8')
            )

            return item
        except:
            return None


    def write(self):
        """Returns the decrypted write credential from the dynamo database"""
        try:
            if self.dynamodb:
                pass
            else:
                self.__connect()

            item = self.table.get_item(
                Key={
                    'credential_id': self.sort_key
                }
            )['Item']

            write_credential = item['write_credential']
            item = json.loads(
                base64.b64decode(write_credential).decode('utf-8')
            )

            return item
        except:
            return None

    def __connect(self):
        self.dynamodb = boto3.resource(
            'dynamodb', region_name='us-west-2'
        )

        self.table = self.dynamodb.Table(self.table_name)

    def __can_get_caller(self, credential):
        """Attempts sts get caller identity using the credential\
        returns truthieness to determine usability"""
        try:
            client = boto3.client('sts',
                aws_access_key_id=credential['AccessKeyId'],
                aws_secret_access_key=credential['SecretAccessKey'],
                aws_session_token=credential['SessionToken'],
                region_name='us-west-2'
            )
            client.get_caller_identity()

            return True
        except:
            return False

    def __is_expired(self, credential):
        """Checks expiration of sts token.  Is truthy."""
        try:
            expiration = credential['Expiration']
            expiration = dateutil.parser.parse(expiration)
            expiration = expiration.strftime('%s')
        except:
            return True


        if expiration < time.time():
            return True
        else:
            return False
