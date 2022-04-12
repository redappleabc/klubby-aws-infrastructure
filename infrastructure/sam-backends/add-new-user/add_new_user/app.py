import json
import requests


def lambda_handler(event, context):
    try:
        console.log('yoyoyo')

        # ip = requests.get("http://checkip.amazonaws.com/")
    except requests.RequestException as e:
        print(e)
        raise e

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }
