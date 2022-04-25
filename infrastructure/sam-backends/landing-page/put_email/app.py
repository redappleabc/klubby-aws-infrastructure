import json
import boto3
from datetime import datetime


import requests


def lambda_handler(event, context):
    TABLE_NAME='klubby-storage-dynamodb-dev-EmailDynamoTable-1OYXRYYJBIJDY'
    try:
        if event['httpMethod'] == 'POST':
            dynamodb = boto3.client('dynamodb')

            print(event)
            body = json.loads(event['body'])
            email = body['email']

            now = datetime.now() # current date and time
            date = now.strftime("%m/%d/%Y,%H:%M:%S")

            dynamodb.put_item(TableName=TABLE_NAME, Item={'email':{'S':email},'date':{'S':date}})

    except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
        print(e)

        raise e

    return {
        "statusCode": 200,
        'headers': {
                'Access-Control-Allow-Origin': '*',
                "Content-Type": "application/json",
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE',
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization, Access-Control-Allow-Headers',
            },
        "body": json.dumps({
            "message": "success",
            # "location": ip.text.replace("\n", "")
        }),
    }
