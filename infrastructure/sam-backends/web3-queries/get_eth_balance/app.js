let response;

const AWS = require('aws-sdk');
const Web3 = require('web3')

const USER_TABLE_SSM_NAME = `user-table-name-${process.env.STAGE}`
const CONTRACT_TABLE_SSM_NAME = `contract-table-name-${process.env.STAGE}`

const RPC_URL="http://35.171.16.213:8545"

//conect to GETH node
const web3 = new Web3(RPC_URL)

//load ABIs
var fs = require('fs');
var erc20ABI = JSON.parse(fs.readFileSync('abi/erc20Abi.json', 'utf8'));
var erc721ABI = JSON.parse(fs.readFileSync('abi/erc721Abi.json', 'utf8'));

// The minimum ABI to get ERC20 Token balance
// const minABI = [
//     // balanceOf
//     {
//       "constant":true,
//       "inputs":[{"name":"_owner","type":"address"}],
//       "name":"balanceOf",
//       "outputs":[{"name":"balance","type":"uint256"}],
//       "type":"function"
//     },
//     // decimals
//     {
//       "constant":true,
//       "inputs":[],
//       "name":"decimals",
//       "outputs":[{"name":"","type":"uint8"}],
//       "type":"function"
//     }
//   ];
  

async function get_ssm_param(ssm_param_name){
    const ssm = new AWS.SSM();
    const response = await ssm.getParameter({
        Name: ssm_param_name
    }).promise();

    console.log(response.Parameter.Value)
    console.log(typeof response.Parameter.Value)

    return response.Parameter.Value
}

//funuction to get eth balance
async function getEthBalance(web3,walletAddress){
    const balance = await web3.eth.getBalance(walletAddress);

    return Web3.utils.fromWei(balance, 'ether')
}

async function getAssetBalance(asset,walletAddress){
    let asset_type = asset.contractType.S

    let balance = -1
    if(asset_type==='erc20'){
        const contract = new web3.eth.Contract(erc20ABI,asset.address.S);
        balance = await contract.methods.balanceOf(walletAddress).call();
    }
    else if(asset_type==='erc721'){
        const contract = new web3.eth.Contract(erc721ABI,asset.address.S);
        balance = await contract.methods.balanceOf(walletAddress).call();

        if(balance > 0){
            console.log('balance',balance,asset.address.S)

            for(let i in balance){
                try {
                    let tokenId = await contract.methods.tokenOfOwnerByIndex(walletAddress,i).call();
                    console.log('tokenId',tokenId)
    
                    let tokenUri = await contract.methods.tokenURI(6332).call();
                    // baseURI = await contract.methods.baseURI().call();
                    console.log('tokenUri',tokenUri)
                    console.log('tokenUri',tokenUri.length)




                }

                catch(e){
                    console.error("error",e)
                    console.log("error",e.message)
                    console.log("error",e.data)
                    console.log("error",Object.keys(e))
                    console.log("error",e)
                }

            }
        }

    }


    // console.log(asset)
    // console.log('balance',balance)
    return balance
}

exports.lambdaHandler = async (event, context) => {
    try {
        //get user table names from ssm
        const user_table_name = await get_ssm_param(USER_TABLE_SSM_NAME)
        const contract_table_name = await get_ssm_param(CONTRACT_TABLE_SSM_NAME)

        //get users from dynamo
        var dynamodb = new AWS.DynamoDB()

        let params = {
            TableName: user_table_name,
        }
        let result = await dynamodb.scan(params).promise()

        //for each user
        for(const element of result.Items){
        // result.Items.forEach(async function (element, index, array) {

            //if user has a wallet
            if(element.wallets && element.wallets.S != ""){
                const walletAddress = element.wallets.S

                //get assets from contract table
                let query_params = {
                    TableName: contract_table_name,
                }
                let result = await dynamodb.scan(query_params).promise()


                //get eth balance
                const ethBalance = await getEthBalance(web3,walletAddress)

                // let updateExpression  = 'set balance_eth = :eth'
                // let expressionValueObj = {":eth": {'N':ethBalance}}
                let assetObj = {}
                let assetList = []
                if(ethBalance > 0){
                    // assetObj['eth'] = {'M': {'balance':{'N':ethBalance},'symbol': {'S': 'ETH'},'name': {'S':'ethereum'}, 'contractType': {'S':'eth'}}}
                    assetList.push({'M': {'balance':{'N':ethBalance},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}})
                    // assetObj['eth'] = {'balance': ethBalance,'symbol': 'ETH','name': 'ethereum'}
                }

                //get balance for each asset
                for(asset of result.Items){
                    let balance = await getAssetBalance(asset,walletAddress)
                    let asset_address = asset.address.S.toLowerCase()
                    //TODO will break with colliding symbols
                    if(balance > 0){
                        // assetObj[asset_address] = {'M': {'balance':{'N':balance},'symbol': {'S':asset.symbol.S},'name': {'S':asset.name.S}, 'contractType': {'S': asset.contractType.S}}}
                        // assetObj[asset_address] = {'balance':balance,'symbol': asset.symbol.S,'name': asset.name.S}
                        assetList.push({'M': {'balance':{'N':balance},'symbol': {'S':asset.symbol.S},'name': {'S':asset.name.S}, 'contractType': {'S': asset.contractType.S},'address': {'S':asset_address}}})
                    }
                    // updateExpression = updateExpression + `, balance_${asset_address} = :${asset_address}`

                }
                // expressionValueObj = {':asset_obj': {'M': assetObj}}
                expressionValueObj = {':asset_list': {'L': assetList}}
                // updateExpression = 'set assets = :asset_obj'
                updateExpression = 'set assets = :asset_list'

                // console.log('assetList',assetList)
                console.log('name',element.username)


                const params = {
                    TableName: user_table_name,
                    Key: {
                        "username": element.username
                    },
                    UpdateExpression: updateExpression,
                    ExpressionAttributeValues: expressionValueObj
                }

                let res = await dynamodb.updateItem(params).promise() 
            }
        }

        response = {
            'statusCode': 200,
            'body': JSON.stringify({
                status: "success",
            })
        }
    } catch (err) {
        console.log(err);
        return err;
    }

    return response
};
