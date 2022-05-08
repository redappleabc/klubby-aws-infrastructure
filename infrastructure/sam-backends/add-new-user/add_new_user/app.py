import json
import boto3

def lambda_handler(event, context):
    TABLE_NAME="klubby-storage-dynamodb-dev-UserTable-IM4YXWAHTLAF"
    
    try:
        username = event['userName']
        email = event['request']['userAttributes']['email']

        dynamodb = boto3.client('dynamodb')
        dynamodb.put_item(TableName=TABLE_NAME, Item={'username':{'S':username},'email':{'S':email}})


        print(username,email)

        return event

    except Exception as e:
        print(e)
        raise e
