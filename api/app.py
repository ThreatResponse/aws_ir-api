#!/usr/bin/python
import os
import json

from chalice import Chalice
from chalicelib import credential

#key compromise plugins
from chalicelib.aws_ir.aws_ir.plugins import revokests_key
from chalicelib.aws_ir.aws_ir.plugins import disableaccess_key

#host compromise plugins
from chalicelib.aws_ir.aws_ir.plugins import gather_host
from chalicelib.aws_ir.aws_ir.plugins import isolate_host
from chalicelib.aws_ir.aws_ir.plugins import snapshotdisks_host
from chalicelib.aws_ir.aws_ir.plugins import stop_host
from chalicelib.aws_ir.aws_ir.plugins import tag_host

app = Chalice(app_name='aws_ir-api')


@app.route('/')
def index():
    return {'AWS_IR-api': 'experimental'}


@app.route('/credential', methods=['POST'], api_key_required=True)
def credential_get():
    """Takes a json post with sort_key and operation\
    Returns key validity based on a number of Checks\
    """
    try:
        post = app.current_request.json_body
        c = credential.Credential(post['sort_key'])
        if post['operation'] == 'read':
            check = c.check('read')
        if post['operation'] == 'write':
            check = c.check('write')
        if check == True:
            return {'status': 'valid'}
        else:
            return {'status': 'invalid'}
    except:
        print("Exception occured while calling")
        return {'status': 'malformed-payload'}

@app.route('/key/{access_key_id}/{plugin}', methods=['POST', 'GET'], api_key_required=True)
def key(access_key_id, plugin):
    """Takes an access key ID and plugin based on plugin will run disable STS"""
    post = app.current_request.json_body

    c = credential.Credential(post['sort_key'])
    print access_key_id

    compromised_resource = {
        'access_key_id': access_key_id,
        'compromise_type': 'KeyCompromise'
    }
    try:
        if c.check('write'):
            aws_credential = c.write_credential
            client = c.aws_client(
                'iam',
                aws_credential,
                'us-west-2'
            )
            try:
                plugin = disableaccess_key.Disableaccess(
                    client=client,
                    compromised_resource=compromised_resource,
                    dry_run=False
                )

                status = plugin.validate()
            except Exception as error:
                status = False
        else:
            status = False
    except:
        status = False
    return {'status': status}
