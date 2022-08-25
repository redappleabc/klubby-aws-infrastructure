import json
import boto3
import os

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
ssm_client = boto3.client('ssm')

#get stage from env var
Stage = os.getenv('STAGE')

def lambda_handler(event, context):
    print(f'event {event}')
 
    #get params from event
    klubname = event['arguments']['klubname']

    #get klub table name from ssm
    response = ssm_client.get_parameter(Name=f'klub-table-name-{Stage}')
    klub_table_name=response['Parameter']['Value']

    #get klub info
    result = dynamodb.get_item(TableName=klub_table_name, Key={'klubname':{'S':klubname}})
    klub_info = result['Item']

    avatar_url = klub_info['avatar_url']['S']
    mainGroupConversationId = klub_info['mainGroupConversationId']['S']
    whaleGroupConversationId = klub_info['whaleGroupConversationId']['S']
    announcementConversationId = klub_info['announcementConversationId']['S']

    #delete avatar_url
    #parse url into bucket name and object key
    bucket_name = avatar_url.split("/")[2][:-17]
    object_name = avatar_url.split("/")[-1]

    response = s3.delete_object(
        Bucket=bucket_name,
        Key=f'klub-avatars/{object_name}'
    )

    #get conversation table name from ssm
    response = ssm_client.get_parameter(Name=f'conversation-table-name-{Stage}')
    conversation_table_name=response['Parameter']['Value']

    #delete mainGroupConversation
    result = dynamodb.delete_item(TableName=conversation_table_name, Key={'id':{'S':mainGroupConversationId}})

    #TODO delete messages associate with conversation?

    #delete whaleGroupConversation
    result = dynamodb.delete_item(TableName=conversation_table_name, Key={'id':{'S':whaleGroupConversationId}})


    #delete announcementConversation
    result = dynamodb.delete_item(TableName=conversation_table_name, Key={'id':{'S':announcementConversationId}})


    #delete klub
    result = dynamodb.delete_item(TableName=klub_table_name, Key={'klubname':{'S':klubname}})

    return {
            "statusCode": 200,
            "body": "yo"
        }













    # if meetsRequirement:
    #     #TODO create user klub bridge

    #     #get userKlubBridge table name from ssm
    #     response = ssm_client.get_parameter(Name=f'userklubbridge-table-name-{Stage}')
    #     table_name=response['Parameter']['Value']

    #     #add row to userKlubBridge Table to join
    #     result = dynamodb.put_item(TableName=table_name, Item={'username':{'S':username},'klubname':{'S':klubname}})
    #     print(f'result {result}')

    #     return {
    #         "statusCode": 200,
    #         "body": json.dumps({
    #             "message": f"{username} joined {klubname}",
    #             "meetsRequirement": meetsRequirement,
    #             "UserKlubBridge": {
    #                 "username": username,
    #                 "klubname": klubname
    #             }
    #         }),
    #     }
    # else:
    #     return {
    #             "statusCode": 200,
    #             "body": json.dumps({
    #                 "message": f"{userName} can not join {klubname}. Does not meet the minimum asset requirement",
    #                 "meetsRequirement": meetsRequirement
    #             }),
    #         }