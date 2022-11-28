import boto3


class S3():
    def __init__(self, bucket_name):
        self.client = boto3.client('s3')
        self.bucket_name = bucket_name