"""
This file is part of lambda function to authorize deployment calls.
"""

import os
import json
import urllib.request
import urllib.error
from authorizer import AuthPolicy


def handle(event, context):
    # Parse event data
    tmp = event['methodArn'].split(':')
    api_gateway_arn_tmp = tmp[5].split('/')
    aws_account_id = tmp[4]

    # Authorize request against app-backend
    data = json.dumps(dict(
        token=event['queryStringParameters']['access_token'],
        resource_id=event['requestContext']['resourceId']
    )).encode()
    url = f'{os.environ["API_URL"]}/auth/deployment/'
    req = urllib.request.Request(url, data)
    req.add_header('Content-Length', len(data))
    req.add_header('Content-Type', 'application/json')
    try:
        resp = urllib.request.urlopen(req, data)
    except urllib.error.HTTPError as e:
        status = e.code
        resp_data = {}
    else:
        status = resp.getcode()
        resp_data = json.load(resp)

    # Create policy
    user_id = resp_data.get('user_id', '00000000-0000-0000-0000-000000000000')
    policy = AuthPolicy(user_id, aws_account_id)
    policy.restApiId = api_gateway_arn_tmp[0]
    policy.region = tmp[3]
    policy.stage = api_gateway_arn_tmp[1]
    context = {}
    if status != 200:
        policy.denyAllMethods()
        context = resp_data
    else:
        policy.allowMethod("GET", event['path'])

    auth_resp = policy.build()
    auth_resp['context'] = context
    return auth_resp
