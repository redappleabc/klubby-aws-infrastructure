import json
import os
import boto3
from boto3.dynamodb.types import TypeDeserializer
from boto3.dynamodb.types import TypeSerializer
# import requests

#get stage from env var
Stage = os.getenv('STAGE')
# Stage = 'dev'

ssm_client = boto3.client('ssm')
dynamodb = boto3.client('dynamodb')
deserializer = TypeDeserializer()
serializer = TypeSerializer()

#TODO get last read from user conversation bridge

def lambda_handler(event, context):
    print(event)

    #get params from event
    username = event['arguments']['username']
    conversationId = event['arguments']['conversationId']

    #get message table name from ssm
    response = ssm_client.get_parameter(Name=f'message-table-name-{Stage}')
    message_table_name=response['Parameter']['Value']

    print(message_table_name)




    # Use the DynamoDB client to query for all songs by artist Arturus Ardvarkian
    response = dynamodb.query(
        TableName=message_table_name,
        KeyConditionExpression='conversationId = :conversationId',
        ExpressionAttributeValues={
            ':conversationId': {'S': conversationId}
        }
    )
    print(response['Items'])