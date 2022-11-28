import boto3
import json
import sys
import pprint

STAGE='dev'
FUNCTION_ARN_SSM_NAME = f'delete-klub-function-arn-{STAGE}'

if __name__ == '__main__':
    #parse cli args
    if len(sys.argv) == 1:
        print("Error: Need to provide klubname")
        exit(-1)

    klubname = sys.argv[1]

    ssm_client = boto3.client('ssm',region_name='us-east-1')
    lambda_client = boto3.client('lambda',region_name='us-east-1')

    #get funciton arn from ssm
    function_arn = ssm_client.get_parameter(Name=FUNCTION_ARN_SSM_NAME)['Parameter']['Value']

    event = {"action": "delete_klub", "arguments": {"klubname": klubname}}

    #invoke function to delete klub
    response = lambda_client.invoke(FunctionName=function_arn,Payload=json.dumps(event))

    # #print result
    pprint.pprint(response)
