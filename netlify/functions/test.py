import json

def handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json"
    }
    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps({"msg": "测试函数成功"})
    }
