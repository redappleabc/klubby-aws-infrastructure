import boto3

#temp


class S3():
    def __init__(self, bucket_name):
        self.client = boto3.client('s3', region_name='us-east-1')
        self.bucket_name = bucket_name