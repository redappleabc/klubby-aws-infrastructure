import boto3


class SSM():
    def __init__(self):
        self.client = boto3.client('ssm', region_name='us-east-1')

    def getParameterValue(param_name):
        response = ssm_client.get_parameter(Name=param_name)
        param_val = response['Parameter']['Value']
        return param_val