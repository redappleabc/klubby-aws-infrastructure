import json
import boto3
import os

# dynamodb = boto3.client('dynamodb')
# ssm_client = boto3.client('ssm')

#get stage from env var
Stage = os.getenv('STAGE')

def lambda_handler(event, context):
    print(f'event {event}')

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "yoooooo",
        }),
    }