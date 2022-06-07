let response;

const AWS = require('aws-sdk');
const Web3 = require('web3')

const TABLE_NAME = "klubby-storage-dynamodb-dev-UserTable-IM4YXWAHTLAF"


//funuction to get eth balance
async function getBalance(web3,walletAddress){
    const balance = await web3.eth.getBalance(walletAddress);

    return balance
}

exports.lambdaHandler = async (event, context) => {
    try {
        //conect to GETH node
        const RPC_URL="http://18.206.231.219:8545"
        const web3 = new Web3(RPC_URL)

        //get users from dynamo
        var dynamodb = new AWS.DynamoDB()

        const params = {
            TableName: TABLE_NAME,
        }
        let result = await dynamodb.scan(params).promise()

        //for each user
        for(const element of result.Items){
        // result.Items.forEach(async function (element, index, array) {
            
            //if user has a wallet
            if(element.wallets && element.wallets.S != ""){
                const walletAddress = element.wallets.S

                //get eth balance
                const balance = await getBalance(web3,walletAddress)

                const params = {
                    TableName: TABLE_NAME,
                    Key: {
                        "username": element.username
                    },
                    UpdateExpression: "set balance_eth = :x",
                    ExpressionAttributeValues: {
                        ":x": {'S':balance}
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
