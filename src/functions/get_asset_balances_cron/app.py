import json
import boto3
from boto3.dynamodb.types import TypeDeserializer
import os

from lib.aws.SSM import SSM
from lib.web3.Web3 import Web3Client
from lib.web3.Web3 import decodeIpfsUrl

dynamodb = boto3.client('dynamodb')
deserializer = TypeDeserializer()

ssm = SSM()
web3 = Web3Client()


Stage = os.getenv('STAGE')

def lambda_handler(event, context):
    print(f'event {event}')

    #get params from ssm 
    user_table_name = ssm.getParameterValue(f'user-table-name-{Stage}')
    contract_table_name = ssm.getParameterValue(f'contract-table-name-{Stage}')

    #get list of possible assets from contract table
    contract_results = dynamodb.scan(TableName=contract_table_name)
    contracts = contract_results['Items']

    #get list of users from user table
    results = dynamodb.scan(TableName=user_table_name)
    user_items = results['Items']

    for user_item in user_items:
        asset_obj = {}

        #if user has wallet
        if 'wallets' in user_item and len(user_item['wallets']['L']) > 0:
            #get user assets
            asset_obj = {}

            for wallet in user_item['wallets']['L']:
                wallet_address = wallet['S']
                print(f'add {wallet_address}')

                eth_balance = web3.get_eth_balance(wallet_address)

                if(eth_balance > 0):
                    if 'ETH' not in asset_obj:
                        # asset_list.append({'M': {'balance':{'N':str(eth_balance)},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}})
                        asset_obj['ETH'] = {'M': {'balance':{'N':str(eth_balance)},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}}
                    else:
                        new_balance = float(eth_balance) + float(asset_obj['ETH']['M']['balance']['N'])
                        # asset_list.append({'M': {'balance':{'N':str(eth_balance)},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}})
                        asset_obj['ETH'] = {'M': {'balance':{'N':str(new_balance)},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}}

                for asset in contracts:
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

        asset_list = list(asset_obj.values())

        #update assets field
        user_item['assets'] = {'L': asset_list}


        #update dynamo record
        result = dynamodb.put_item(TableName=user_table_name, Item=user_item)

        print(user_item)


    return json.dumps({
        "statusCode": 200,
        "body": {
        },
    })