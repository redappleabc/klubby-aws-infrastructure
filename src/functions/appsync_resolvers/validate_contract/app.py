import json
import boto3
import os

from lib.aws.SSM import SSM
from lib.web3.Web3 import Web3Client

ssm = SSM()
web3 = Web3Client()

#get stage from env var
Stage = os.getenv('STAGE')
    

def lambda_handler(event, context):
    #parse address from event
    address = event['arguments']['address']
    contractType = event['arguments']['contractType']

    # address = '0x714599f7604144a3fE1737c440a70fc0fD6503ea' #20
    # address = '0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce' #20
    # address = '0x06012c8cf97BEaD5deAe237070F9587f8E7A266d' #721
    # address = '0x495f947276749Ce646f68AC8c248420045cb7b5e' #1155
    # contractType = 'erc20'


    #check that checksum is valid address
    if not web3.isValid(address):
        return json.dumps({
            "statusCode": 200,
            "body": {
                "validAddress": False,
                "message": 'invalid address'
            },
        })

    # isERC20Contract, asset_name, symbol = web3.isERC20Contract(address)
    # print(f'isERC20Contract {isERC20Contract}')

    # isERC721Contract, asset_name, symbol = web3.isERC721Contract(address)
    # print(f'isERC721Contract {isERC721Contract}')
    
    if contractType == 'erc20':
        isERC20Contract, asset_name, symbol, totalSupply = web3.isERC20Contract(address)

        if not isERC20Contract:
            return json.dumps({
                "statusCode": 200,
                "body": {
                    "validAddress": False,
                },
            })

    elif contractType == 'erc721':
        isERC721Contract, asset_name, symbol, totalSupply = web3.isERC721Contract(address)

        if not isERC721Contract:
            return json.dumps({
                "statusCode": 200,
                "body": {
                    "validAddress": False,
                },
            })

    # else if contractType == 'erc1155':
    #     res = web3.isERC1155Contract(address)
    #     print(f'res {res}')


    ### write contract address to contract table if not already there ###

    #get contract table name from ssm
    contract_table_name = ssm.getParameterValue(f'contract-table-name-{Stage}')

    dynamodb = boto3.resource('dynamodb')

    #check if contract is already in table
    table = dynamodb.Table(contract_table_name)

    item = {
        "address": web3.toChecksumAddress(address),
        "contractType": contractType,
        "name": asset_name,
        "symbol": symbol
    }


    response = table.put_item(TableName=contract_table_name,Item=item)#,ConditionExpression='attribute_not_exists(address)')


    return json.dumps({
        "statusCode": 200,
        "body": {
            "validAddress": True,
                "contractInfo": {
                    "asset_name": asset_name,
                    "symbol": symbol,
                    "totalSupply": totalSupply
                }
        },
    })