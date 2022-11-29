from web3 import Web3
import requests
import json


RPC_URL="http://35.171.16.213:8545"
INFURA_URL="https://mainnet.infura.io/v3/2b81405266ea4180b99daeff72498e0c"

#load abi files


#list files in current directory
import os
print(os.listdir('/opt'))
print(os.listdir('/opt/pyhthon'))
print(os.listdir('/opt/lib'))
print('WEWEWEWE')



# returns JSON object as
# a dictionary
erc20ABI = {}
with open('opt/python/lib/web3/abi/erc20Abi.json') as f:
    erc20ABI = json.load(f)

erc721ABI = {}
with open('opt/python/lib/web3/abi/erc721Abi.json') as f:
    erc721ABI = json.load(f)
    print('YOYOYOYO')
    print(erc721ABI)


def decodeIpfsUrl(ipfs_url):
    #check if string starts with 'https://'
    if ipfs_url.startswith('https://'):
        return ipfs_url

    # prefix = "https://mainnet.infura-ipfs.io/ipfs/"
    prefix = "https://cloudflare-ipfs.com/ipfs/"

    hash = ipfs_url.replace('ipfs://', '')

    return prefix + hash

class Web3Client():
    def __init__(self):
        # self.client = Web3(Web3.HTTPProvider(RPC_URL))
        self.client = Web3(Web3.HTTPProvider(INFURA_URL))

    def get_eth_balance(self,wallet_address):
        wei_eth_balance = self.client.eth.get_balance(wallet_address)
        eth_balance = self.client.fromWei(wei_eth_balance, 'ether')

        return eth_balance

    def getAssetBalance(self,asset,wallet_address):
        # print(asset)

        if asset['contractType'] == 'erc20':
            asset_address = self.client.toChecksumAddress(asset['address'])
            contract = self.client.eth.contract(abi=erc20ABI,address=asset_address)
            balance = contract.functions.balanceOf(wallet_address).call()
            decimal = contract.functions.decimals().call()
            return balance / 10**decimal

        elif asset['contractType'] == 'erc721':
            asset_address = self.client.toChecksumAddress(asset['address'])
            contract = self.client.eth.contract(abi=erc721ABI,address=asset_address)
            balance = contract.functions.balanceOf(wallet_address).call()

            tokens = []
            for i in range(0,balance):
                tokenId = contract.functions.tokenOfOwnerByIndex(wallet_address,i).call()

                tokenUri = contract.functions.tokenURI(tokenId).call()

                #decode ipfs uri
                decodedUrl = decodeIpfsUrl(tokenUri)

                print(f'decodedUrl {decodedUrl}')

                r = requests.get(decodedUrl).json()

                #pull ipfs image url and decode
                imageUrl = decodeIpfsUrl(r['image'])

                tokens.append({'M': {'tokenId': {'N': str(tokenId)}, 'tokenUri': {'S': tokenUri},'imageUrl': {'S': imageUrl}} })

            return (balance,tokens)