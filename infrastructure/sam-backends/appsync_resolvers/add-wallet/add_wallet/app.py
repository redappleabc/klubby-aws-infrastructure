import json
import os
import boto3
from boto3.dynamodb.types import TypeDeserializer
from web3 import Web3
# import requests

#get stage from env var
Stage = os.getenv('STAGE')
# Stage = 'dev'

ssm_client = boto3.client('ssm')
dynamodb = boto3.client('dynamodb')
deserializer = TypeDeserializer()


RPC_URL="http://35.171.16.213:8545"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

#load abi files
  
# returns JSON object as 
# a dictionary
erc20ABI = {}
with open('./abi/erc20Abi.json') as f:
    erc20ABI = json.load(f)

erc721ABI = {}
with open('./abi/erc721Abi.json') as f:
    erc721ABI = json.load(f)
  

def get_asset_balance(asset,wallet_address):
    # print(asset)

    if asset['contractType'] == 'erc20':

        asset_address = w3.toChecksumAddress(asset['address']) 
        contract = w3.eth.contract(abi=erc20ABI,address=asset_address)
        balance = contract.functions.balanceOf(wallet_address).call()


    elif asset['contractType'] == 'erc721':
        asset_address = w3.toChecksumAddress(asset['address']) 
        contract = w3.eth.contract(abi=erc721ABI,address=asset_address)
        balance = contract.functions.balanceOf(wallet_address).call()

    print(asset['name'],balance)

    return balance  

def get_eth_balance(wallet_address):
    wei_eth_balance = w3.eth.get_balance(wallet_address)
    eth_balance = w3.fromWei(wei_eth_balance, 'ether')

    return eth_balance

def lambda_handler(event, context):
    # print(event)

    wallet_address = event['arguments']['address']
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

    #add wallet to user item
    user_item['wallets'] = {'S' : wallet_address}

    #get user assets
    asset_list = []

    eth_balance = get_eth_balance(wallet_address)

    if(eth_balance > 0):
        asset_list.append({'M': {'balance':{'N':str(eth_balance)},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}})

    #get list of possible assets from contract table
    contact_results = dynamodb.scan(TableName=contract_table_name)

    for asset in contact_results['Items']:
        clean_data = {k: deserializer.deserialize(v) for k,v in asset.items()}

        balance = get_asset_balance(clean_data,wallet_address)

        if balance > 0:
            asset_list.append({'M': {'balance':{'N':str(balance)},'symbol': {'S':asset['symbol']['S']},'name': {'S':asset['name']['S']}, 'contractType': {'S': asset['contractType']['S']}, 'address': {'S':asset_address}}})
    
    #update assets field
    user_item['assets'] = {'L': asset_list}


    #update dynamo record
    result = dynamodb.put_item(TableName=user_table_name, Item=user_item)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }
