import json
import boto3
import os

dynamodb = boto3.client('dynamodb')
ssm_client = boto3.client('ssm')

#get stage from env var
Stage = os.getenv('STAGE')

def query_klub_table(klubname):
    #get klub table name from ssm
    response = ssm_client.get_parameter(Name=f'klub-table-name-{Stage}')
    table_name=response['Parameter']['Value']

    #query the table
    results = dynamodb.get_item(TableName=table_name, Key={'klubname':{'S':klubname}})

    #get asset symbot from results
    assetSymbol = results['Item']['assetSymbol']['S'].lower()

    #get min asset requirement to join klub from results
    minimumAmountForMainGroup = results['Item']['minimumAmountForMainGroup']['N']

    return (assetSymbol,minimumAmountForMainGroup)

def checkMinAssetRequirement(username,klubname):
    assetSymbol,minimumAmountForMainGroup = query_klub_table(klubname)
    
    #get user table name from ssm
    response = ssm_client.get_parameter(Name=f'user-table-name-{Stage}')
    table_name=response['Parameter']['Value']

    #get users amount of asset
    res = dynamodb.get_item(TableName=table_name, Key={'username':{'S':username}})
    #TODO change this to num type
    amountOwned = res['Item'][f'balance_{assetSymbol}']['S']
    print(f'amountOwned {amountOwned}')

    #compare amountOwned to min requirement
    if amountOwned >= minimumAmountForMainGroup:
        return True
    else:
        return False

def lambda_handler(event, context):
    print(f'event {event}')
 
    #get params from event
    username = event['arguments']['username']
    klubname = event['arguments']['klubname']

    meetsRequirement = checkMinAssetRequirement(username,klubname)

    if meetsRequirement:
        #TODO create user klub bridge

        #get userKlubBridge table name from ssm
        response = ssm_client.get_parameter(Name=f'userklubbridge-table-name-{Stage}')
        table_name=response['Parameter']['Value']

        #add row to userKlubBridge Table to join
        result = dynamodb.put_item(TableName=table_name, Item={'username':{'S':username},'klubname':{'S':klubname}})
        print(f'result {result}')

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"{username} joined {klubname}",
                "meetsRequirement": meetsRequirement,
                "UserKlubBridge": {
                    "username": username,
                    "klubname": klubname
                }
            }),
        }
    else:
        return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": f"{userName} can not join {klubname}. Does not meet the minimum asset requirement",
                    "meetsRequirement": meetsRequirement
                }),
            }