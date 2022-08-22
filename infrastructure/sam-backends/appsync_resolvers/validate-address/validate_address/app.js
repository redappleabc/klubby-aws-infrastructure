let response;

const AWS = require('aws-sdk');
const Web3 = require('web3')

const RPC_URL="http://18.206.231.219:8545"

const CONTRACT_TABLE_SSM_NAME = `contract-table-name-${process.env.STAGE}`

// The minimum ABI to get ERC20 Token balance
const minABI = [
    {
        "constant": true,
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_spender",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_from",
                "type": "address"
            },
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            },
            {
                "name": "_spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "payable": true,
        "stateMutability": "payable",
        "type": "fallback"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "spender",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
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

exports.lambdaHandler = async (event, context) => {
    try {
        //conect to GETH node
        const web3 = new Web3(RPC_URL)

        let address = event.arguments.address
        let contractType = event.arguments.contractType

        try{
            const contract = new web3.eth.Contract(minABI,address);
            console.log(contract)

            var totalSupply = await contract.methods.totalSupply().call();
            var name = await contract.methods.name().call();
            var symbol = await contract.methods.symbol().call();

            console.log(totalSupply,name,symbol)
        }

        catch (err) {
            return JSON.stringify({
                'statusCode': 200,
                'body': {
                    err: err,
                    validAddress: false
                }
            })
        }

        try{
            //get contract table name from ssm
            const table_name = await get_ssm_param(CONTRACT_TABLE_SSM_NAME)

            console.log(table_name)

            //write address to contract table if not already there
            var params = {
                ConditionExpression: 'attribute_not_exists(address)',
                TableName: table_name,
                Item: {
                    'address' : {S: address},
                    'contractType' : {S: contractType},
                    'name': {S: name}
                }
            };

            var dynamodb = new AWS.DynamoDB()
            let res = await dynamodb.putItem(params).promise()
            console.log(res)
        }
        catch(err){
            if (err.message === "The conditional request failed") {
                console.log("Contract already exists in contract table");
            }
            else{
                console.log(err);
                return err;
            }
        }


        return JSON.stringify({
            'statusCode': 200,
            'body': {
                validAddress: true,
                contractInfo: {
                    name,
                    symbol,
                    totalSupply,
                }

            }
        })

    } catch (err) {
        console.log(err);
        return err;
    }
};
