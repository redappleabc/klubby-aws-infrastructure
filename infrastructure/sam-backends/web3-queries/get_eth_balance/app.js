let response;

const AWS = require('aws-sdk');
const Web3 = require('web3')

const USER_TABLE_SSM_NAME = `user-table-name-${process.env.STAGE}`
const CONTRACT_TABLE_SSM_NAME = `contract-table-name-${process.env.STAGE}`

const RPC_URL="http://35.171.16.213:8545"
const INFURA_URL="https://mainnet.infura.io/v3/2b81405266ea4180b99daeff72498e0c"

//conect to GETH node
// const web3 = new Web3(RPC_URL)
const web3 = new Web3(INFURA_URL)

//load ABIs
var fs = require('fs');
var erc20ABI = JSON.parse(fs.readFileSync('abi/erc20Abi.json', 'utf8'));
var erc721ABI = JSON.parse(fs.readFileSync('abi/erc721Abi.json', 'utf8'));
  

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

        return ['erc20',balance]
    }

    else if(asset_type==='erc721'){
        const contract = new web3.eth.Contract(erc721ABI,asset.address.S);
        let tokens = []
        balance = await contract.methods.balanceOf(walletAddress).call();

        if(balance > 0){
            for(let i in balance){
                try {
                    let tokenId = await contract.methods.tokenOfOwnerByIndex(walletAddress,i).call();
                    // console.log('tokenId',tokenId)
    
                    let tokenUri = await contract.methods.tokenURI(tokenId).call();
                    // baseURI = await contract.methods.baseURI().call();
                    // console.log('tokenUri',tokenUri)
                    tokens.push({tokenId,tokenUri})


                }

                catch(e){
                    console.error("error",e)
                    console.log("error",e.message)
                    // console.log("error",e.data)
                    // console.log("error",Object.keys(e))
                    // console.log("error",e)
                }

            }
        }

        return ['erc721',balance,tokens]
    }
}

exports.lambdaHandler = async (event, context) => {
    try {
        console.log('starting')
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

            //if user has a wallet
            if(element.wallets && element.wallets.length != 0){
                const walletList = element.wallets.L

                //get assets from contract table
                let query_params = {
                    TableName: contract_table_name,
                }
                let result = await dynamodb.scan(query_params).promise()

                let assetObj = {}
                // let assetList = []

                //for each wallet
                for(wallet_obj of walletList){

                    let walletAddress = wallet_obj.S

                    //get eth balance
                    const ethBalance = await getEthBalance(web3,walletAddress)

                    if(ethBalance > 0){
                        if(!('ETH' in assetObj)){
                            // assetList.push({'M': {'balance':{'N':ethBalance},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}})
                            assetObj['ETH'] = {'M': {'balance':{'N':ethBalance},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}}

                        }
                        else{
                            let new_balance = parseFloat(ethBalance) + parseFloat(assetObj['ETH']['M']['balance']['N'])
                            assetObj['ETH'] = {'M': {'balance':{'N':new_balance.toString()},'symbol': {'S': 'ETH'},'name': {'S':'Ethereum'}, 'contractType': {'S':'eth'},'address': {'S':'n/a'}}}

                        }
                    }

                    //get balance for each asset
                    for(asset of result.Items){
                        let balance_result = await getAssetBalance(asset,walletAddress)

                        if(balance_result[0] === 'erc20'){
                            let balance = balance_result[1]

                            let asset_address = asset.address.S.toLowerCase()
                            //TODO will break with colliding symbols
                            if(balance > 0){
                                if(!(asset_address in assetObj)){
                                    // assetList.push({'M': {'balance':{'N':balance},'symbol': {'S':asset.symbol.S},'name': {'S':asset.name.S}, 'contractType': {'S': asset.contractType.S},'address': {'S':asset_address}}})
                                    assetObj[asset_address] = {'M': {'balance':{'N':balance},'symbol': {'S':asset.symbol.S},'name': {'S':asset.name.S}, 'contractType': {'S': asset.contractType.S},'address': {'S':asset_address}}}
                                }
                                else{
                                    let new_balance = parseFloat(ethBalance) + parseFloat(assetObj[asset_address]['M']['balance']['N'])
                                    assetObj[asset_address] = {'M': {'balance':{'N':new_balance.toString()},'symbol': {'S':asset.symbol.S},'name': {'S':asset.name.S}, 'contractType': {'S': asset.contractType.S},'address': {'S':asset_address}}}
                                }
                            }
                            // updateExpression = updateExpression + `, balance_${asset_address} = :${asset_address}`
                        }
                        else if(balance_result[0] === 'erc721'){
                            let balance = balance_result[1]
                            let tokens = balance_result[2]


                            if(balance > 0){
                                if(!(asset_address in assetObj)){
                                    // assetList.push({'M': {'balance':{'N':balance},'symbol': {'S':asset.symbol.S},'name': {'S':asset.name.S}, 'contractType': {'S': asset.contractType.S},'address': {'S':asset_address},'tokens': {'L':tokens}}})
                                    assetObj[asset_address] = {'M': {'balance':{'N':balance},'symbol': {'S':asset.symbol.S},'name': {'S':asset.name.S}, 'contractType': {'S': asset.contractType.S},'address': {'S':asset_address},'tokens': {'L':tokens}}}
                                }
                                else{
                                    let new_balance = parseFloat(ethBalance) + parseFloat(assetObj[asset_address]['M']['balance']['N'])
                                    let new_tokens = tokens + assetObj[asset_address]['M']['tokens']['L']

                                    assetObj[asset_address] = {'M': {'balance':{'N':new_balance.toString()},'symbol': {'S':asset.symbol.S},'name': {'S':asset.name.S}, 'contractType': {'S': asset.contractType.S},'address': {'S':asset_address},'tokens': {'L':new_tokens}}}

                                }
                            }
                        }
                    }
                }

                //create assetList
                let assetList = []
                for(asset in assetObj){
                    assetList.push(assetObj[asset])
                }


                // expressionValueObj = {':asset_obj': {'M': assetObj}}
                expressionValueObj = {':asset_list': {'L': assetList}}
                // updateExpression = 'set assets = :asset_obj'
                updateExpression = 'set assets = :asset_list'

                console.log('assetList',assetList)
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
