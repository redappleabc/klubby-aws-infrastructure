let response;

const AWS = require('aws-sdk');
const Web3 = require('web3')

const USER_TABLE_SSM_NAME = `user-table-name-${process.env.STAGE}`
const CONTRACT_TABLE_SSM_NAME = `contract-table-name-${process.env.STAGE}`

const RPC_URL="http://18.206.231.219:8545"

// KINSHU_ADDRESS = "0xA2b4C0Af19cC16a6CfAcCe81F192B024d625817D"
// SANSHU_ADDRESS = "0xc73c167e7a4ba109e4052f70d5466d0c312a344d"
// RAKU_ADDRESS = "0x714599f7604144a3fE1737c440a70fc0fD6503ea"

//conect to GETH node
const web3 = new Web3(RPC_URL)

//load ABIs
var fs = require('fs');
var erc20ABI = JSON.parse(fs.readFileSync('abi/erc20Abi.json', 'utf8'));
var erc721ABI = JSON.parse(fs.readFileSync('abi/erc721Abi.json', 'utf8'));

// The minimum ABI to get ERC20 Token balance
const minABI = [
    // balanceOf
    {
      "constant":true,
      "inputs":[{"name":"_owner","type":"address"}],
      "name":"balanceOf",
      "outputs":[{"name":"balance","type":"uint256"}],
      "type":"function"
    },
    // decimals
    {
      "constant":true,
      "inputs":[],
      "name":"decimals",
      "outputs":[{"name":"","type":"uint8"}],
      "type":"function"
    }
  ];
  

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

    return balance
}

//funuction to get kishu inu balance
async function getKishuBalance(web3,walletAddress){
    const contract = new web3.eth.Contract(minABI,KINSHU_ADDRESS);

    const balance = await contract.methods.balanceOf(walletAddress).call();

    return balance
}

//funuction to get sanshu inu balance
async function getSanshuBalance(web3,walletAddress){
    const contract = new web3.eth.Contract(minABI,SANSHU_ADDRESS);

    const balance = await contract.methods.balanceOf(walletAddress).call();

    return balance
}

//funuction to get raku coin balance
async function getRakuBalance(web3,walletAddress){
    const contract = new web3.eth.Contract(minABI,RAKU_ADDRESS);

    const balance = await contract.methods.balanceOf(walletAddress).call();

    return balance
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
    }


    console.log(asset)
    console.log('balance',balance)
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
                if(ethBalance > 0){
                    assetObj['eth'] = {'M': {'balance':{'N':ethBalance},'symbol': {'S': 'ETH'},'name': {'S':'ethereum'}}}
                    // assetObj['eth'] = {'balance': ethBalance,'symbol': 'ETH','name': 'ethereum'}
                }

                //get balance for each asset
                for(asset of result.Items){
                    let balance = await getAssetBalance(asset,walletAddress)
                    let asset_address = asset.address.S
                    //TODO will break with colliding symbols
                    if(balance > 0){
                        assetObj[asset_address] = {'M': {'balance':{'N':balance},'symbol': {'S':asset.symbol.S},'name': {'S':asset.name.S}}}
                        // assetObj[asset_address] = {'balance':balance,'symbol': asset.symbol.S,'name': asset.name.S}

                    }
                    // updateExpression = updateExpression + `, balance_${asset_address} = :${asset_address}`

                }
                expressionValueObj = {':asset_obj': {'M': assetObj}}
                updateExpression = 'set assets = :asset_obj'
                console.log(updateExpression)
                console.log(expressionValueObj)

 
                // const kishuBalance = await getKishuBalance(web3,walletAddress)
                // const sanshuBalance = await getSanshuBalance(web3,walletAddress)
                // const rakuBalance = await getRakuBalance(web3,walletAddress)


                const params = {
                    TableName: user_table_name,
                    Key: {
                        "username": element.username
                    },
                    UpdateExpression: updateExpression,
                    ExpressionAttributeValues: expressionValueObj
                }

                let res = await dynamodb.updateItem(params).promise() 

                // const params = {
                //     TableName: user_table_name,
                //     Key: {
                //         "username": element.username
                //     },
                //     UpdateExpression: "set balance_eth = :x, balance_kishu = :kishu, balance_sanshu = :sanshu, balance_raku = :raku",
                //     ExpressionAttributeValues: {
                //         ":x": {'S':ethBalance},
                //         ":kishu": {'S':kishuBalance},
                //         ":sanshu": {'S':sanshuBalance},
                //         ":raku": {'S':rakuBalance}
                //     }
                // }

                // let res = await dynamodb.updateItem(params).promise()
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
