from web3 import Web3

class Web3Client():
    def __init__(self):
        # self.client = Web3(Web3.HTTPProvider(RPC_URL))
        self.client = Web3(Web3.HTTPProvider(INFURA_URL))

    def getParameterValue(self,param_name):
        response = self.client.get_parameter(Name=param_name)
        param_val = response['Parameter']['Value']
        return param_val


def decodeIpfsUrl(ipfs_url):
    #check if string starts with 'https://'
    if ipfs_url.startswith('https://'):
        return ipfs_url

    # prefix = "https://mainnet.infura-ipfs.io/ipfs/"
    prefix = "https://cloudflare-ipfs.com/ipfs/"

    hash = ipfs_url.replace('ipfs://', '')

    return prefix + hash