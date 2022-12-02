from web3 import Web3
import requests
import json

RPC_URL="http://35.171.16.213:8545"
INFURA_URL="https://mainnet.infura.io/v3/2b81405266ea4180b99daeff72498e0c"

#load abi files
#TODO can probably just use import
erc20ABI = {}
with open('/opt/python/lib/web3/abi/erc20Abi.json') as f:
    erc20ABI = json.load(f)

erc721ABI = {}
with open('/opt/python/lib/web3/abi/erc721Abi.json') as f:
    erc721ABI = json.load(f)

erc1155ABI = {}
with open('/opt/python/lib/web3/abi/erc1155Abi.json') as f:
    erc1155ABI = json.load(f)

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

    def isValid(self,address):
        checksum = self.client.toChecksumAddress(address)
        return self.client.isAddress(checksum)

    def toChecksumAddress(self,address):
        return self.client.toChecksumAddress(address)

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


    def isERC20Contract(self,address):
        try:
            checksum = self.client.toChecksumAddress(address)

            #get contract
            contract = self.client.eth.contract(address=checksum, abi=erc20ABI)

            #get name
            name = contract.functions.name().call()

            #get symbol
            symbol = contract.functions.symbol().call()

            #get decimals
            decimals = contract.functions.decimals().call()

            #get totalSupply
            totalSupply = contract.functions.totalSupply().call()

            #get balanceOf
            balanceOf = contract.functions.balanceOf("0x29D7d1dd5B6f9C864d9db560D72a247c178aE86B").call()

            #get allowance
            allowance = contract.functions.allowance("0x29D7d1dd5B6f9C864d9db560D72a247c178aE86B", "0x29D7d1dd5B6f9C864d9db560D72a247c178aE86B").call()

        except Exception as e:
            print(e)
            return False, '', '', 0

        return True, name, symbol, totalSupply

    def isERC721Contract(self,address):
        try:
            checksum = self.client.toChecksumAddress(address)

            #get contract
            contract = self.client.eth.contract(address=checksum, abi=erc721ABI)

            #get name
            name = contract.functions.name().call()

            #get symbol
            symbol = contract.functions.symbol().call()

            #get totalSupply
            totalSupply = contract.functions.totalSupply().call()

            #get balanceOf
            balanceOf = contract.functions.balanceOf("0x29D7d1dd5B6f9C864d9db560D72a247c178aE86B").call()

            #get supportsInterface
            supportsInterface = contract.functions.supportsInterface('0x80ac58cd').call()

        except Exception as e:
            print(e)
            return False, '', '', 0

        return True, name, symbol, totalSupply

    def isERC1155Contract(self,address):
        try:
            checksum = self.client.toChecksumAddress(address)

            #get contract
            contract = self.client.eth.contract(address=checksum, abi=erc1155ABI)

            #get ApprovalForAll
            # ApprovalForAll = contract.functions.ApprovalForAll("0x29D7d1dd5B6f9C864d9db560D72a247c178aE86B","0x29D7d1dd5B6f9C864d9db560D72a247c178aE86B",False).call()

            #get balanceOf
            balanceOf = contract.functions.balanceOf("0x29D7d1dd5B6f9C864d9db560D72a247c178aE86B",0).call()

            #get uri
            uri = contract.functions.uri(0).call()

            #get supportsInterface
            supportsInterface = contract.functions.supportsInterface('0x80ac58cd').call()

        except Exception as e:
            print(e)
            return False

        return True