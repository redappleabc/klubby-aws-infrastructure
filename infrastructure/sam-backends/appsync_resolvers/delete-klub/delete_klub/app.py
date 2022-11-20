import json
import boto3
import os

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
ssm_client = boto3.client('ssm')

#get stage from env var
Stage = os.getenv('STAGE')

def lambda_handler(event, context):
    try:
        print(f'event {event}')

        #get params from event
        klubname = event['arguments']['klubname']

        #get klub table name from ssm
        response = ssm_client.get_parameter(Name=f'klub-table-name-{Stage}')
        klub_table_name=response['Parameter']['Value']

        #get conversation table name from ssm
        response = ssm_client.get_parameter(Name=f'conversation-table-name-{Stage}')
        conversation_table_name=response['Parameter']['Value']

        #get message table name from ssm
        response = ssm_client.get_parameter(Name=f'message-table-name-{Stage}')
        message_table_name=response['Parameter']['Value']

        #get UserKlubBridge table name from ssm
        response = ssm_client.get_parameter(Name=f'userklubbridge-table-name-{Stage}')
        userklubbridge_table_name=response['Parameter']['Value']

        #get klub info
        result = dynamodb.get_item(TableName=klub_table_name, Key={'klubname':{'S':klubname}})
        klub_info = result['Item']

        avatar_url = klub_info['avatar_url']['S']
        mainGroupConversationId = klub_info['mainGroupConversationId']['S']
        whaleGroupConversationId = klub_info['whaleGroupConversationId']['S']
        announcementConversationId = klub_info['announcementConversationId']['S']


        # ---- delete avatar_url ----
        #parse url into bucket name and object key
        bucket_name = avatar_url.split("/")[2][:-17]
        object_name = avatar_url.split("/")[-1]

        response = s3.delete_object(
            Bucket=bucket_name,
            Key=f'klub-avatars/{object_name}'
        )

        # ---- delete mainGroupConversation ----
        result = dynamodb.delete_item(TableName=conversation_table_name, Key={'id':{'S':mainGroupConversationId}})

        #delete messages associated with conversation
        result = dynamodb.scan(TableName=message_table_name,FilterExpression=f'conversationId = :mainGroupConversationId',ExpressionAttributeValues={':mainGroupConversationId': {'S': mainGroupConversationId}})

        for message in result['Items']:
            result = dynamodb.delete_item(TableName=message_table_name, Key={'id': message['id'],'conversationId': message['conversationId'],})

        # ---- delete whaleGroupConversation ----
        result = dynamodb.delete_item(TableName=conversation_table_name, Key={'id':{'S':whaleGroupConversationId}})

        #delete messages associated with conversation
        result = dynamodb.scan(TableName=message_table_name,FilterExpression=f'conversationId = :whaleGroupConversationId',ExpressionAttributeValues={':whaleGroupConversationId': {'S': whaleGroupConversationId}})

        for message in result['Items']:
            result = dynamodb.delete_item(TableName=message_table_name, Key={'id': message['id'],'conversationId': message['conversationId'],})

        # ---- delete announcementConversation ----
        result = dynamodb.delete_item(TableName=conversation_table_name, Key={'id':{'S':announcementConversationId}})

        #delete messages associated with conversation
        result = dynamodb.scan(TableName=message_table_name,FilterExpression=f'conversationId = :announcementConversationId',ExpressionAttributeValues={':announcementConversationId': {'S': announcementConversationId}})

        for message in result['Items']:
            result = dynamodb.delete_item(TableName=message_table_name, Key={'id': message['id'],'conversationId': message['conversationId'],})

        # ---- delete User Klub associations in UserKlubBridge Table ----
        #delete user klub associations that have this klub
        result = dynamodb.scan(TableName=userklubbridge_table_name,FilterExpression=f'klubname = :klubname',ExpressionAttributeValues={':klubname': {'S': klubname}})
        for klub_member in result['Items']:
            result = dynamodb.delete_item(TableName=userklubbridge_table_name, Key={'klubname': klub_member['klubname'],'username': klub_member['username'],})
        print(result)

        # --- delete klub ---
        result = dynamodb.delete_item(TableName=klub_table_name, Key={'klubname':{'S':klubname}})

    except Exception as e:
        return json.dumps({
            "statusCode": 500,
            "body": {
                "error": f'{e}'
            }
        })

    return json.dumps({
        "statusCode": 200,
        "body": {
            "url_info": result
        }
    })
