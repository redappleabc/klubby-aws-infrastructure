import json
import boto3
import os

def lambda_handler(event, context):

    try:
        Stage = os.getenv('STAGE')

        ssm_client = boto3.client('ssm')
        dynamodb = boto3.client('dynamodb')

        response = ssm_client.get_parameter(Name=f'user-table-name-{Stage}')

        TABLE_NAME=response['Parameter']['Value']

        username = event['userName']
        email = event['request']['userAttributes']['email']

        dynamodb.put_item(TableName=TABLE_NAME, Item={'username':{'S':username},'email':{'S':email}})

        print(username,email)

        return event

    except Exception as e:
        print(e)
        raise e
