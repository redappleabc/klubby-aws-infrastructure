let response;

const AWS = require('aws-sdk');
const Web3 = require('web3')

const USER_TABLE_SSM_NAME = `user-table-name-${process.env.STAGE}`

const RPC_URL="http://18.206.231.219:8545"

KINSHU_ADDRESS = "0xA2b4C0Af19cC16a6CfAcCe81F192B024d625817D"
SANSHU_ADDRESS = "0xc73c167e7a4ba109e4052f70d5466d0c312a344d"
RAKU_ADDRESS = "0x714599f7604144a3fE1737c440a70fc0fD6503ea"

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

exports.lambdaHandler = async (event, context) => {
    try {
        //conect to GETH node
        const web3 = new Web3(RPC_URL)

        //get user table name from ssm
        const table_name = await get_ssm_param(USER_TABLE_SSM_NAME)

        //get users from dynamo
        var dynamodb = new AWS.DynamoDB()

        const params = {
            TableName: table_name,
        }
        let result = await dynamodb.scan(params).promise()

        //for each user
        for(const element of result.Items){
        // result.Items.forEach(async function (element, index, array) {

            //if user has a wallet
            if(element.wallets && element.wallets.S != ""){
                const walletAddress = element.wallets.S

                //get eth balance
                const ethBalance = await getEthBalance(web3,walletAddress)
                const kishuBalance = await getKishuBalance(web3,walletAddress)
                const sanshuBalance = await getSanshuBalance(web3,walletAddress)
                const rakuBalance = await getRakuBalance(web3,walletAddress)


                const params = {
                    TableName: table_name,
                    Key: {
                        "username": element.username
                    },
                    UpdateExpression: "set balance_eth = :x, balance_kishu = :kishu, balance_sanshu = :sanshu, balance_raku = :raku",
                    ExpressionAttributeValues: {
                        ":x": {'S':ethBalance},
                        ":kishu": {'S':kishuBalance},
                        ":sanshu": {'S':sanshuBalance},
                        ":raku": {'S':rakuBalance}
                    }
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
