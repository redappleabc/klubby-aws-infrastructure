import json
import boto3
import os

s3_client = boto3.client('s3')
ssm_client = boto3.client('ssm')


#get stage from env var
Stage = os.getenv('STAGE')

def lambda_handler(event, context):
    try:
        print(f'event {event}')

        #get klub table name from ssm
        response = ssm_client.get_parameter(Name=f'klub-avatar-bucket-name-{Stage}')
        bucket_name=response['Parameter']['Value']

        # bucket="klubby-prod-artifacts-bucketInfo"
        key="/brenden-test/brenden-test"

        params = {"Bucket": bucket_name,"Key": key,"Content-Type": 'text/plain;charset=UTF-8'}

        # result = s3_client.generate_presigned_post(Bucket=bucket_name,Key=key)
        result = s3_client.generate_presigned_url(ClientMethod="put_object",Params=params)

        print(result)

    except Exception as e:
        return {
            "statusCode": 500,
            "body": "\"" + json.dumps({
                "error": f"{e}",
            }) + "\"",
        }

    return json.dumps({
        "statusCode": 200,
        "body": {
            "url_info": result
        }
    })

    # return {
    #     "statusCode": 200,
    #     "body": "\"" + json.dumps({
    #         "url_info": "yo",
    #     }) + "\"",
    # }