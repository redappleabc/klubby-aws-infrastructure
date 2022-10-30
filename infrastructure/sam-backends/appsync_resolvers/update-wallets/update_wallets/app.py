import json
import os
import boto3
from boto3.dynamodb.types import TypeDeserializer
from boto3.dynamodb.types import TypeSerializer
from web3 import Web3
import requests

#get stage from env var
Stage = os.getenv('STAGE')
# Stage = 'dev'

ssm_client = boto3.client('ssm')
dynamodb = boto3.client('dynamodb')
deserializer = TypeDeserializer()
serializer = TypeSerializer()



RPC_URL="http://35.171.16.213:8545"
INFURA_URL="https://mainnet.infura.io/v3/2b81405266ea4180b99daeff72498e0c"

# w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

#load abi files
  
# returns JSON object as 
# a dictionary
erc20ABI = {}
with open('./abi/erc20Abi.json') as f:
    erc20ABI = json.load(f)

erc721ABI = {}
with open('./abi/erc721Abi.json') as f:
    erc721ABI = json.load(f)
  
def decodeIpfsUrl(ipfs_url):
    prefix = "https://mainnet.infura-ipfs.io/ipfs/"
    hash = ipfs_url.replace('ipfs://', '')

    return prefix + hash

def get_asset_balance(asset,wallet_address):
    # print(asset)

    if asset['contractType'] == 'erc20':

        asset_address = w3.toChecksumAddress(asset['address']) 
        contract = w3.eth.contract(abi=erc20ABI,address=asset_address)
        balance = contract.functions.balanceOf(wallet_address).call()

        return balance

    elif asset['contractType'] == 'erc721':
        asset_address = w3.toChecksumAddress(asset['address']) 
        contract = w3.eth.contract(abi=erc721ABI,address=asset_address)
        balance = contract.functions.balanceOf(wallet_address).call()

        tokens = []
        for i in range(0,balance):
            tokenId = contract.functions.tokenOfOwnerByIndex(wallet_address,i).call()

            tokenUri = contract.functions.tokenURI(tokenId).call()

            #decode ipfs uri
            decoddedUrl = decodeIpfsUrl(tokenUri)

            r = requests.get(decoddedUrl).json()

            #pull ipfs image url and decode
            imageUrl = decodeIpfsUrl(r['image'])

            tokens.append({'M': {'tokenId': {'N': tokenId}, 'tokenUri': {'S': tokenUri},'imageUrl': {'S': imageUrl}} })


        return (balance,tokens)

def get_eth_balance(wallet_address):
    wei_eth_balance = w3.eth.get_balance(wallet_address)
    eth_balance = w3.fromWei(wei_eth_balance, 'ether')

    return eth_balance

def lambda_handler(event, context):
    # print(event)

    wallet_list = event['arguments']['wallets']
    username = event['arguments']['username']
    
    #get user table name from ssm
    response = ssm_client.get_parameter(Name=f'user-table-name-{Stage}')
    user_table_name=response['Parameter']['Value']

    #get contract table name from ssm
    response = ssm_client.get_parameter(Name=f'contract-table-name-{Stage}')
    contract_table_name=response['Parameter']['Value']

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
        eth_balance = get_eth_balance(wallet_address)

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
                balance = get_asset_balance(clean_data,wallet_address)

                if balance > 0:
                    if asset_address not in asset_obj:
                        # asset_list.append({'M': {'balance':{'N':str(balance)},'symbol': {'S':asset['symbol']['S']},'name': {'S':asset['name']['S']}, 'contractType': {'S': asset['contractType']['S']}, 'address': asset['address']}})
                        asset_obj[asset_address] = {'M': {'balance':{'N':str(balance)},'symbol': {'S':asset['symbol']['S']},'name': {'S':asset['name']['S']}, 'contractType': {'S': asset['contractType']['S']}, 'address': asset['address']}}

                    else:
                        new_balance = float(balance) + float(asset_obj[asset_address]['M']['balance']['N'])

                        asset_obj[asset_address] = {'M': {'balance':{'N':str(new_balance)},'symbol': {'S':asset['symbol']['S']},'name': {'S':asset['name']['S']}, 'contractType': {'S': asset['contractType']['S']}, 'address': asset['address']}}

            elif clean_data['contractType'] == 'erc721':
                balance,tokens = get_asset_balance(clean_data,wallet_address)


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