
import os
import requests
import json
from chalice import Chalice
from chalicelib import credential

#The aws_ir modules we need to drive the API

#key compromise plugins
from chalicelib.aws_ir.aws_ir.plugins import gather_host
#from aws_ir.plugins import revokests_key

#host compromise plugins
from chalicelib.aws_ir.aws_ir.plugins import gather_host
from chalicelib.aws_ir.aws_ir.plugins import isolate_host
from chalicelib.aws_ir.aws_ir.plugins import snapshotdisks_host
from chalicelib.aws_ir.aws_ir.plugins import stop_host
from chalicelib.aws_ir.aws_ir.plugins import tag_host

#to-do find a way to async gather memory

app = Chalice(app_name='aws_ir-api')


@app.route('/')
def index():
    #credential.Credential('fhsdfdsfkjhfs')
    return {'AWS_IR-api': 'experimental'}

@app.route('/credential', methods=['POST'], api_key_required=True)
def credential_get():
    try:
        post = app.current_request.json_body
        c = credential.Credential(post['sort_key'])
        if post['operation']:
            check = c.check(post['operation'])
        if check == True:
            return {'status': 'valid'}
        else:
            return {'status': 'invalid'}
    except:
        print("Exception occured while calling")
        return {'status': 'malformed-payload'}

@app.route('/key/{plugin}', methods=['POST, GET'], api_key_required=True)
def credential_get(plugin):
    pass
