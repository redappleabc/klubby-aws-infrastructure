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

    print('yoyoyoyo',results)

    #get asset symbot from results
    assetSymbol = results['Item']['assetSymbol']['S'].lower()
    address = results['Item']['contractAddress']['S'].lower()

    #get min asset requirement to join klub from results
    minimumAmountForMainGroup = results['Item']['minimumAmountForMainGroup']['N']
    minimumAmountForWhaleGroup = results['Item']['minimumAmountForWhaleGroup']['N']

    return (assetSymbol,address,minimumAmountForMainGroup,minimumAmountForWhaleGroup)

def checkMinAssetRequirement(username,klubname):
    assetSymbol,address,minimumAmountForMainGroup,minimumAmountForWhaleGroup = query_klub_table(klubname)

    #get user table name from ssm
    response = ssm_client.get_parameter(Name=f'user-table-name-{Stage}')
    table_name=response['Parameter']['Value']

    #get users amount of asset
    res = dynamodb.get_item(TableName=table_name, Key={'username':{'S':username}})

    #if klub is public return and user doesnt have wallet return true,false
    if minimumAmountForMainGroup == '0' and 'assets' not in res['Item']:
        return True, False

    #if eth
    if address == 'n/a':
        address = 'eth'

    assets = res['Item']['assets']

    try:
        amountOwned = float(assets['M'][address]['M']['balance']['N'])
    except Exception as e:
        amountOwned = 0


    #compare amountOwned to min requirement
    if amountOwned >= float(minimumAmountForMainGroup):
        print('owns enough for main')
        if amountOwned >= float(minimumAmountForWhaleGroup):
            return True, True
        return True, False

    else:
        print('doesnt own enough')
        return False, False

def lambda_handler(event, context):
    print(f'event {event}')
 
    #get params from event
    username = event['arguments']['username']
    klubname = event['arguments']['klubname']

    meetsRequirement,meetsWhaleRequirement = checkMinAssetRequirement(username,klubname)

    if meetsRequirement:
        #TODO create user klub bridge

        #get userKlubBridge table name from ssm
        response = ssm_client.get_parameter(Name=f'userklubbridge-table-name-{Stage}')
        table_name=response['Parameter']['Value']

        #dynamically add field if the meet whale requirement
        if meetsWhaleRequirement:
            putItem = {'username':{'S':username},'klubname':{'S':klubname},'whale':{'B':'true'}}
        else:
            putItem = {'username':{'S':username},'klubname':{'S':klubname}}

        #add row to userKlubBridge Table to join
        result = dynamodb.put_item(TableName=table_name, Item=putItem)
        print(f'result {result}')

        return json.dumps({
            "statusCode": 200,
            "body": {
                "message": f"{username} joined {klubname}",
                "meetsRequirement": meetsRequirement,
                "UserKlubBridge": {
                    "username": username,
                    "klubname": klubname
                }
            },
        })
    else:
        return json.dumps({
                "statusCode": 501,
                "body": {
                    "message": f"{username} can not join {klubname}. Does not meet the minimum asset requirement",
                    "meetsRequirement": meetsRequirement
                },
            })