#!/usr/bin/python
import os
import json

from chalice import Chalice
from chalice import BadRequestError
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
app.debug = True


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
        app.log.debug("Instantiating credentials for {sort_key}").format(
            sort_key = sort_key
        )
        read = c.check('read')
        write = c.check('write')
        #Instead of checking the operation attempt to retreive and report both.
        return {
            'credential': {'read': read, 'write': write}
        }
    except:
        app.log.error("Error while attempting credential retrieval.")
        raise BadRequestError("Key could not be validated.")


@app.route(
    '/keys/{access_key_id}/{plugin}',
    methods=['POST', 'GET'],
    api_key_required=True
)
def keys(access_key_id, plugin):
    """Takes an access key ID and plugin based on plugin will run disable STS"""
    try:
        post = app.current_request.json_body

        c = credential.Credential(post['sort_key'])
        compromised_resource = {
            'access_key_id': access_key_id,
            'compromise_type': 'KeyCompromise'
        }

        aws_credential = c.write_credential
        client = c.aws_client(
            'iam',
            aws_credential,
            'us-west-2'
        )

        plugin = disableaccess_key.Disableaccess(
            client=client,
            compromised_resource=compromised_resource,
            dry_run=False
        )
        status = plugin.validate()

        return {'disabled': status}

    except KeyError:
        raise BadRequestError("Route takes an access_key_id and plugin.")

    except:
        raise BadRequestError("{} failed".format(plugin))



