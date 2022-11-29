import os
import boto3
from boto3.dynamodb.types import TypeDeserializer
from boto3.dynamodb.types import TypeSerializer

#get stage from env var
Stage = os.getenv('STAGE')
# Stage = 'dev'

dynamodb = boto3.client('dynamodb')
deserializer = TypeDeserializer()
serializer = TypeSerializer()

from lib.aws.SSM import SSM
from lib.Web3 import Web3Client
from lib.Web3 import decodeIpfsUrl

ssm = SSM()
web3 = Web3Client()


def lambda_handler(event, context):
    # print(event)

    wallet_list = event['arguments']['wallets']
    username = event['arguments']['username']
    
    #get params from ssm
    user_table_name = ssm.getParameterValue(f'user-table-name-{Stage}')
    contract_table_name = ssm.getParameterValue(f'contract-table-name-{Stage}')

    #query the table
    results = dynamodb.get_item(TableName=user_table_name, Key={'username':{'S':username}})

    #get the user item from the results
    user_item = results['Item']

    #TODO rn just overwitting address, make it a list and append
    #serialize wallet list for dynamo
    serialized_wallet_list = serializer.serialize(wallet_list)

    #get list of possible assets from contract table
    contact_results = dynamodb.scan(TableName=contract_table_name)

    #get user assets
    # asset_list = []
    asset_obj = {}

    for wallet_address in wallet_list:
        eth_balance = web3.get_eth_balance(wallet_address)

        if(eth_balance > 0):
            if 'ETH' not in asset_obj:
                # asset_list.append({'M': {'balance':{'N':str(eth_balance)},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}})
                asset_obj['ETH'] = {'M': {'balance':{'N':str(eth_balance)},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}}
            else:
                new_balance = float(eth_balance) + float(asset_obj['ETH']['M']['balance']['N'])
                # asset_list.append({'M': {'balance':{'N':str(eth_balance)},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}})
                asset_obj['ETH'] = {'M': {'balance':{'N':str(new_balance)},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}}


        for asset in contact_results['Items']:
            clean_data = {k: deserializer.deserialize(v) for k,v in asset.items()}
            asset_address = asset['address']['S']

            if clean_data['contractType'] == 'erc20':
                balance = web3.getAssetBalance(asset=clean_data,wallet_address=wallet_address)

                if balance > 0:
                    if asset_address not in asset_obj:
                        # asset_list.append({'M': {'balance':{'N':str(balance)},'symbol': {'S':asset['symbol']['S']},'name': {'S':asset['name']['S']}, 'contractType': {'S': asset['contractType']['S']}, 'address': asset['address']}})
                        asset_obj[asset_address] = {'M': {'balance':{'N':str(balance)},'symbol': {'S':asset['symbol']['S']},'name': {'S':asset['name']['S']}, 'contractType': {'S': asset['contractType']['S']}, 'address': asset['address']}}

                    else:
                        new_balance = float(balance) + float(asset_obj[asset_address]['M']['balance']['N'])

                        asset_obj[asset_address] = {'M': {'balance':{'N':str(new_balance)},'symbol': {'S':asset['symbol']['S']},'name': {'S':asset['name']['S']}, 'contractType': {'S': asset['contractType']['S']}, 'address': asset['address']}}

            elif clean_data['contractType'] == 'erc721':
                balance,tokens = web3.getAssetBalance(asset=clean_data,wallet_address=wallet_address)


                if balance > 0:
                    if asset_address not in asset_obj:
                        # asset_list.append({'M': {'balance':{'N':str(balance)},'symbol': {'S':asset['symbol']['S']},'name': {'S':asset['name']['S']}, 'contractType': {'S': asset['contractType']['S']}, 'address': asset['address']}})
                        asset_obj[asset_address] = {'M': {'balance':{'N':str(balance)},'symbol': {'S':asset['symbol']['S']},'name': {'S':asset['name']['S']}, 'contractType': {'S': asset['contractType']['S']}, 'address': asset['address'],'tokens': {'L': tokens}}}

                    else:
                        new_balance = float(balance) + float(asset_obj[asset_address]['M']['balance']['N'])
                        new_tokens = tokens + asset_obj[asset_address]['M']['tokens']['L']

                        asset_obj[asset_address] = {'M': {'balance':{'N':str(new_balance)},'symbol': {'S':asset['symbol']['S']},'name': {'S':asset['name']['S']}, 'contractType': {'S': asset['contractType']['S']}, 'address': asset['address'],'tokens': {'L': new_tokens}}}



    # print("asset_obj",asset_obj)
    # print("list",asset_obj.values())

    asset_list = list(asset_obj.values())


    #update assets field
    user_item['assets'] = {'L': asset_list}

    #add wallet to user item
    user_item['wallets'] = serialized_wallet_list


    #update dynamo record
    result = dynamodb.put_item(TableName=user_table_name, Item=user_item)

    print(user_item)

    #need to change to plain list to work with appsync query in console
    # user_item['assets'] = asset_list

    #deserialize the data
    user_clean_data = {k: deserializer.deserialize(v) for k,v in user_item.items()}

    return user_clean_data