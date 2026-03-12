import base64
import urllib
import requests
import json
import os

# 从 Netlify 环境变量读取密钥（避免硬编码）
API_KEY = os.getenv("BAIDU_API_KEY")
SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")

def get_access_token():
    """生成百度AI鉴权Token"""
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY
    }
    try:
        response = requests.post(url, params=params)
        token = response.json().get("access_token")
        return token
    except Exception as e:
        print(f"获取Token失败: {e}")
        return None

def get_file_content_as_base64(image_data):
    """将二进制图片数据转为BASE64（适配前端上传）"""
    try:
        content = base64.b64encode(image_data).decode("utf8")
        return content
    except Exception as e:
        print(f"BASE64编码失败: {e}")
        return None

def handler(event, context):
    """Netlify Functions 核心处理函数"""
    # 1. 处理跨域
    headers = {
        "Access-Control-Allow-Origin": "*",  # 生产环境建议限定域名
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }

    # 2. 仅处理POST请求
    if event["httpMethod"] != "POST":
        return {
            "statusCode": 405,
            "headers": headers,
            "body": json.dumps({"error": "仅支持POST请求"})
        }

    try:
        # 3. 解析前端上传的图片数据
        body = json.loads(event["body"])
        image_base64 = body.get("image")  # 前端传BASE64字符串，或二进制转BASE64
        if not image_base64:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "未上传图片"})
            }

        # 4. 获取百度AI Token并调用人脸检测接口
        token = get_access_token()
        if not token:
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({"error": "获取百度Token失败"})
            }

        # 5. 构造百度API请求
        url = f"https://aip.baidubce.com/rest/2.0/face/v3/detect?access_token={token}"
        payload = json.dumps({
            "image": image_base64,
            "image_type": "BASE64",
            "face_field": "age,expression,face_shape,gender,beauty,glasses,landmark,landmark150,quality,eye_status,emotion,face_type,mask,spoofing,feature"
        }, ensure_ascii=False)

        baidu_headers = {"Content-Type": "application/json"}
        response = requests.post(
            url,
            headers=baidu_headers,
            data=payload.encode("utf-8")
        )

        # 6. 返回百度API的响应结果
        return {
            "statusCode": 200,
            "headers": headers,
            "body": response.text
        }

    except Exception as e:
        # 异常处理
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": f"服务器错误: {str(e)}"})
        }
