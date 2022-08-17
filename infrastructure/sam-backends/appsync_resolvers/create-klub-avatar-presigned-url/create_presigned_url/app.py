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

        #Format object_key from event info
        klubname = event['arguments']['klubname']
        object_key=f"klub-avatars/{klubname}"


        #get klub table name from ssm
        response = ssm_client.get_parameter(Name=f'klub-avatar-bucket-name-{Stage}')
        bucket_name=response['Parameter']['Value']

        params = {"Bucket": bucket_name,"Key": object_key,"ContentType": 'text/plain;charset=UTF-8',"ACL": "public-read"}

        # result = s3_client.generate_presigned_post(Bucket=bucket_name,Key=key)
        result = s3_client.generate_presigned_url(ClientMethod="put_object",Params=params)

        print(result)

    except Exception as e:
        return json.dumps({
            "statusCode": 500,
            "body": {
                "error": f'{e}'
            }
        })

    return json.dumps({
        "statusCode": 200,
        "body": {
            "url_info": result
        }
    })