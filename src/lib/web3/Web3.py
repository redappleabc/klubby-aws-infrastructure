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


    def isERC20Contract(self,address):
        try:
            print('yoyoyoyoyoshmo')
            #get contract
            contract = self.client.eth.contract(address=address, abi=erc20ABI)

            #get name
            name = contract.functions.name().call()

            #get symbol
            symbol = contract.functions.symbol().call()

            #get decimals
            decimals = contract.functions.decimals().call()

            #get totalSupply
            totalSupply = contract.functions.totalSupply().call()

            #get balanceOf
            balanceOf = contract.functions.balanceOf(address).call()

            #get allowance
            allowance = contract.functions.allowance(address, address).call()

            #get owner
            owner = contract.functions.owner().call()

            #get paused
            paused = contract.functions.paused().call()

            #get cap
            cap = contract.functions.cap().call()

            #get mintingFinished
            mintingFinished = contract.functions.mintingFinished().call()

            #get minter
            minter = contract.functions.minter().call()

            #get pauser
            pauser = contract.functions.pauser().call()

            #get transferOwnership
            transferOwnership = contract.functions.transferOwnership(address).call()

            #get renounceOwnership
            renounceOwnership = contract.functions.renounceOwnership().call()

            #get addMinter
            addMinter = contract.functions.addMinter(address).call()

            #get renounceMinter
            renounceMinter = contract.functions.renounceMinter().call()

            #get addPauser
            addPauser = contract.functions.addPauser(address).call()

            #get renouncePauser
            renouncePauser = contract.functions.renouncePauser().call()

            #get pause
            pause = contract.functions.pause().call()

            #get unpause
            unpause = contract.functions.unpause().call()

            #get mint
            mint = contract.functions.mint(address, 1).call()

            #get finishMinting
            finishMinting = contract.functions.finishMinting().call()

            #get burn
            burn = contract.functions.burn(1).call()

            #get burnFrom
            burnFrom = contract.functions.burnFrom(address, 1).call()

            #get increaseAllowance
            increaseAllowance = contract.functions.increaseAllow

        except Exception as e:
            print(e)
            return False

        return True