let response;

const AWS = require('aws-sdk');
const Web3 = require('web3')

const RPC_URL="http://35.171.16.213:8545"
const INFURA_URL="https://mainnet.infura.io/v3/2b81405266ea4180b99daeff72498e0c"

const CONTRACT_TABLE_SSM_NAME = `contract-table-name-${process.env.STAGE}`

//load ABIs
var fs = require('fs');
var erc20ABI = JSON.parse(fs.readFileSync('abi/erc20Abi.json', 'utf8'));
var erc721ABI = JSON.parse(fs.readFileSync('abi/erc721Abi.json', 'utf8'));


async function get_ssm_param(ssm_param_name){
    const ssm = new AWS.SSM();
    const response = await ssm.getParameter({
        Name: ssm_param_name
    }).promise();

    return response.Parameter.Value
}

//https://ethereum.stackexchange.com/questions/44880/erc-165-query-on-erc-721-implementation

exports.lambdaHandler = async (event, context) => {
    try {
        //conect to GETH node
        // const web3 = new Web3(RPC_URL)
        const web3 = new Web3(INFURA_URL)

        let address = event.arguments.address
        let contractType = event.arguments.contractType

		try{
			if(contractType === "erc20"){
                const contract = new web3.eth.Contract(erc20ABI,address);
				
                var totalSupply = await contract.methods.totalSupply().call();
                var name = await contract.methods.name().call();
                var symbol = await contract.methods.symbol().call();

				//ensure is erc20 by calling functions
				//TODO check all functions in ABI
				await contract.methods.decimals().call();

				//ensure not erc721 by calling functions
				let erc_721_failed = true
				try{
					const contract2 = new web3.eth.Contract(erc721ABI,address);
					let res = await contract2.methods.supportsInterface('0x80ac58cd').call();
					erc_721_failed = false
				}
				catch (err){
					console.log('ERC721 test failed as expected')
				}

				if(!erc_721_failed){
					return JSON.stringify({
						'statusCode': 200,
						'body': {
							err: err,
							validAddress: false
						}
					})
				}

                console.log(totalSupply,name,symbol)
            }

            else if(contractType === "erc721"){
                const contract = new web3.eth.Contract(erc721ABI,address);

                var totalSupply = await contract.methods.totalSupply().call();
                var name = await contract.methods.name().call();
                var symbol = await contract.methods.symbol().call();

                //ensure is erc721 by calling functions
				//TODO check all functions in ABI
				// 01ffc9a7
				let res = await contract.methods.supportsInterface('0x80ac58cd').call();
				console.log('supports erc721 (0x80ac58cd)?:',res)

                console.log(totalSupply,name,symbol)
            }
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
                    'name': {S: name},
                    'symbol': {S: symbol}
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
