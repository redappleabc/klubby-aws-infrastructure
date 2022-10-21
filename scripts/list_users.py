import boto3
from boto3.dynamodb.types import TypeDeserializer
import pprint

STAGE='dev'
USER_TABLE_SSM_NAME = f'user-table-name-{STAGE}'

deserializer = TypeDeserializer()


if __name__ == '__main__':
    ssm_client = boto3.client('ssm',region_name='us-east-1')
    dynamo_client = boto3.client('dynamodb',region_name='us-east-1')

    #get table name from ssm
    table_name = ssm_client.get_parameter(Name=USER_TABLE_SSM_NAME)['Parameter']['Value']

    #scan user table
    response = dynamo_client.scan(TableName=table_name)

    #print result
    for user in response['Items']:
        #remove data types from dynamo response
        clean_data = {k: deserializer.deserialize(v) for k,v in user.items()}
        
        # print('')
        # pprint.pprint(clean_data)

        pprint.pprint(clean_data['username'])