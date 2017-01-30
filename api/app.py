#!/usr/bin/python
import os
import json
import botocore

from chalice import Chalice
from chalice import BadRequestError
from chalice import UnauthorizedError
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
        # app.log.debug("Instantiating credentials for {sort_key}").format(
        #     sort_key = sort_key
        # )
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

        aws_credential = c.get_write()
        client = c.aws_client(
            'iam',
            aws_credential,
            'us-west-2'
        )

        if plugin == 'disable':
            plugin_client = disableaccess_key.Disableaccess(
                client=client,
                compromised_resource=compromised_resource,
                dry_run=False
            )
        elif plugin == 'revoke_sts':
            plugin_client = revokests_key.RevokeSTS(
                client=client,
                compromised_resource=compromised_resource,
                dry_run=False
            )

        return {plugin: plugin_client.validate()}

    except KeyError:
        raise BadRequestError("Route takes an access_key_id and plugin.")

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            raise UnauthorizedError(e)
        else:
            raise Exception(e)

    except Exception as e:
        print e
        raise BadRequestError("{} failed - {}".format(plugin, e))

@app.route(
    '/hosts/{instance_id}/{plugin}',
    methods=['POST', 'GET'],
    api_key_required=True
)
def hosts(instance_id, plugin):
    """
    Takes an instance id and plugin in the params
    Requires a json post with compromised resource data
    to hand off to aws_ir host based plugins
    """
    try:
        post = app.current_request.json_body

        c = credential.Credential(post['sort_key'])

        compromised_resource = {
            'instance_id': post['instance_id'],
            'region': post['region'],
            'case_number': post['case_number'],
            'public_ip_address': post['public_ip_address'],
            'private_ip_address':  post['private_ip_address'],
            'vpc_id':  post['vpc_id'],
            'compromise_type': 'HostCompromise'
        }

        aws_credential = c.get_write()
        client = c.aws_client(
            'ec2',
            aws_credential,
            post['region']
        )

        if plugin == 'isolate_host':
            plugin_client = isolate_host.Isolate(
                client=client,
                compromised_resource=compromised_resource,
                dry_run=False
            )
        elif plugin == 'tag_host':
            plugin_client = tag_host.Tag(
                client=client,
                compromised_resource=compromised_resource,
                dry_run=False
            )

        return {plugin: plugin_client.validate()}

    except KeyError:
        raise BadRequestError(
            "Route requires instance_id, region, case_number, private\
            public_ip_address, vpc_id, compromise_type, sort_key"
        )

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            raise UnauthorizedError(e)
        else:
            raise Exception(e)

    except Exception as e:
        print e
        raise BadRequestError("{} failed - {}".format(plugin, e))

