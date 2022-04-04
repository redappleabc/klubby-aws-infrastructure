from __future__ import print_function
import json
import boto3
import os
import urllib3
from base64 import b64encode

codepipeline_client = boto3.client('codepipeline')
integration_user = os.environ['INTEGRATION_AUTH_USER']
integration_pass = os.environ['INTEGRATION_AUTH_PASS']
integration_type = os.environ['INTEGRATION_TYPE']
user_pass = integration_user+":"+integration_pass
region = os.environ['AWS_REGION']
repo_id = 'bjudson1/klubby-react-app'

def lambda_handler(event, context):
    message = event['Records'][0]['Sns']['Message']
    data = json.loads(message)
    print (data)

    commit_id = data['commitId']
    state = data['status']
    stage = 'dev'
    
    #     if data['detail']['state'].upper() in [ "SUCCEEDED" ]:
    #         state = "success"
    #     elif data['detail']['state'].upper() in [ "STARTED", "STOPPING", "STOPPED", "SUPERSEDED" ]:
    #         state = "pending"
    #     else:
    #         state = "error"

    url = "https://api.github.com/repos/" + repo_id + "/statuses/" + commit_id
    build_status={}
    build_status['state'] = state
    build_status['context'] = f'amplify-deployment-{stage}'
    build_status['description'] = f'webapp deploymen {stage}'
    #todo add aplify app id to make target url go there
    build_status['target_url'] = "https://" + region + ".console.aws.amazon.com/amplify/"
    # # else:
    # #     return()

    encode_user_pass = b64encode(user_pass.encode()).decode()
    http = urllib3.PoolManager()
    r = http.request('POST', url,
    headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'Curl/0.1', 'Authorization' : 'Basic %s' %  encode_user_pass},
    body=json.dumps(build_status).encode('utf-8')
    )
    print(r.data)
    return message