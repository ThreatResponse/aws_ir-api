
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

@app.route('/credential', methods=['POST'], api_key_required=False)
def credential_get():
    post = app.current_request.json_body

    c = credential.Credential(post['sort_key'])
    print c.table_name

    try:
        check = c.check('read')
        if check == True:
            return {'status': 'valid'}
        else:
            return {'status': 'invalid'}
    except:
        print("Exception occured while calling")
        return {'status': 'invalid'}

# The view function above will return {"hello": "world"}
# whenver you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.json_body
#     # Suppose we had some 'db' object that we used to
#     # read/write from our database.
#     # user_id = db.create_user(user_as_json)
#     return {'user_id': user_id}
#
# See the README documentation for more examples.
#
