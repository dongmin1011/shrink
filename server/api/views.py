import base64
import hashlib
import hmac

import requests
import json
import time
import random
from django.core.cache import cache


from django.http import JsonResponse
import os

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from dotenv import load_dotenv


NCP_ACCESS_KEY = os.getenv('NCP_ACCESS_KEY')
NCP_SECRET_KEY = os.getenv('NCP_SECRET_KEY')
NCP_SENS_SERVICE_ID = os.getenv('NCP_SENS_SERVICE_ID')
NCP_SENS_SEND_PHONE_NO = os.getenv('NCP_SENS_SEND_PHONE_NO')



def index(req):
    if req.method == "GET":
        return JsonResponse({'response': True})

@csrf_exempt
@require_http_methods(["POST"])
def send_auth_code(req):
    data = json.loads(req.body)
    phone = data.get('phone')

    timestamp = int(time.time() * 1000)
    timestamp = str(timestamp)

    url = "https://sens.apigw.ntruss.com"
    uri = f"/sms/v2/services/{NCP_SENS_SERVICE_ID}/messages"

    def generate_code():
        return str(random.randint(100000, 999999))

    def generate_signature(NCP_SECRET_KEY, NCP_ACCESS_KEY, timestamp, url, uri):
        NCP_SECRET_KEY = bytes(NCP_SECRET_KEY, 'UTF-8')
        method = "POST"
        message = method + " " + uri + "\n" + timestamp + "\n" + NCP_ACCESS_KEY
        message = bytes(message, 'UTF-8')
        signingKey = base64.b64encode(hmac.new(NCP_SECRET_KEY, message, digestmod=hashlib.sha256).digest())
        return signingKey

    header = {
        "Content-Type": "application/json; charset=utf-8",
        "x-ncp-apigw-timestamp": timestamp,
        "x-ncp-iam-access-key": NCP_ACCESS_KEY,
        "x-ncp-apigw-signature-v2": generate_signature(NCP_SECRET_KEY, NCP_ACCESS_KEY, timestamp, url, uri)
    }

    EXPIRE_SEC = 60 * 3

    auth_code = generate_code()
    cache.set(phone, auth_code, timeout = EXPIRE_SEC)
    content = f"ai-market 인증번호는 {auth_code} 입니다."
    print('content >> ', content)

    payload = {
        "type": "SMS",
        "contentType": "COMM",
        "countryCode": "82",
        "from": NCP_SENS_SEND_PHONE_NO,
        "content": content,
        "messages": [{"to": phone}],
    }

    res = requests.post(url + uri, headers=header, data=json.dumps(payload))
    datas = json.loads(res.text)

    return JsonResponse({
        "message": "인증번호가 전송되었습니다.",
        "data": datas
    })


@csrf_exempt
@require_http_methods(["POST"])
def check_auth_code(req):
    data = json.loads(req.body)
    phone = data.get('phone')
    code = data.get('code')

    auth_code = cache.get(phone)
    print('phone, auth_code, code >> ', phone, auth_code, code)



    if auth_code is not None:
        if auth_code == code:
            cache.delete(phone)

            return JsonResponse({
                "status": "success",
                "phone": phone,
                "message": "인증되었습니다."
            })
        else:
            return JsonResponse({
                "status": "fail",
                "phone": phone,
                "message": "인증번호가 일치하지 않습니다."
            }, status=401)
    else:
        return JsonResponse({
                "status": "fail",
                "phone": phone,
                "message": "인증번호가 존재하지 않습니다."
        }, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def set_value(req):
    try:
        data = json.loads(req.body)
        key = data.get('key')
        value = data.get('value')

        cache.set(key, value, timeout = 10)

        return JsonResponse({
            "status": "success",
            "key": key,
            "value": value
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

@require_http_methods(["GET"])
def get_value(req, key):
    value = cache.get(key)

    if value is not None:
        return JsonResponse({
            "status": "success",
            "key": key,
            "value": value
        })
    else:
        return JsonResponse({"key": key, "value": value}, status=404)

