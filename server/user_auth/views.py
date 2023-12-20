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

from .utils.user_utils import generate_random_nickname
from .models import User


import jwt
import datetime
from django.conf import settings
from django.contrib.auth import authenticate, login

from django.contrib.auth.hashers import make_password, check_password

from .decorators import token_required



import boto3


def upload_file(file, file_name):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    try:
        s3.upload_fileobj(
            file,
            settings.AWS_S3_STORAGE_BUCKET_NAME,
            file_name,
            ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type}
        )

        file_url = f'https://{settings.AWS_S3_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_name}'
        return file_url
    except Exception as e:
        print("Something Happened: ", e)
        return None

@csrf_exempt
@require_http_methods(["POST"])
def update_profile_image(req):
    user_id = req.POST.get('user_id')
    image_file = req.FILES.get('image')

    try:
        user = User.objects.get(id=user_id)
        file_name = f'profile_images/{user_id}'
        file_url = upload_file(image_file, file_name)

        if file_url:
            user.profile_url = file_url
            user.save()
            return JsonResponse({'status': 'success', 'message': '프로필 이미지가 변경되었습니다.'})
        else:
            return JsonResponse({'status': 'error', 'message': '이미지 업로드 실패'}, status=500)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '사용자가 존재하지 않습니다.'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def update_nickname(request, user_id):
    new_nickname = json.loads(request.body).get('new_nickname')

    try:
        user = User.objects.get(id=user_id)
        user.nickname = new_nickname
        user.save()
        return JsonResponse({'status': 'success', 'message': '닉네임이 변경되었습니다.'})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '사용자가 존재하지 않습니다.'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def update_password(req):
    data = json.loads(req.body)
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    try:
        user = User.objects.get(id=user_id)
        if check_password(current_password, user.password):
            user.password = make_password(new_password)
            user.save()
            return JsonResponse({'status': 'success', 'message': '비밀번호가 변경되었습니다.'})
        else:
            return JsonResponse({'status': 'fail', 'message': '현재 비밀번호가 일치하지 않습니다.'}, status=401)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '사용자가 존재하지 않습니다.'}, status=404)



@csrf_exempt
@require_http_methods(["POST"])
def login(req):
    data = json.loads(req.body)
    phone = data.get('phone')
    password = data.get('password')

    try:
        user = User.objects.get(phone=phone)
        if check_password(password, user.password):

            exp = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            payload = {
                'user_id': str(user.id),
                'exp': exp
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            return JsonResponse({
                'status': 'success',
                'message': '로그인에 성공했습니다.',
                'user' : {
                    'nickname': user.nickname,
                    'profile_url': user.profile_url,
                },
                'token': token
            }, status=200)
        else:
            return JsonResponse({
                'status': 'fail',
                'message': '비밀번호가 일치하지 않습니다.'
            }, status=401)
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '사용자가 존재하지 않습니다.'
        }, status=401)


@csrf_exempt
@require_http_methods(["POST"])
def register(req):
    try:
        data = json.loads(req.body)

        '''
        설명: nickname, profile_url은 초기 회원가입시 입력받지 않고 랜덤으로 지정해주기 때문에 None으로 초기화한다.
        작성일: 2023.12.19
        작성자: yujin
        '''
        phone = data.get('phone')
        password = data.get('password')
        nickname = None
        profile_url = None

        if nickname is None:
            nickname = generate_random_nickname()

        '''
        설명: 프로필 이미지를 랜덤으로 생성하는 dicebear api를 사용한다.
            랜덤 프로필 이미지를 서버에서 구현하면 클라이언트는 편하겠지만, 
            추후 랜덤 이미지를 변경하고자 할 때 서버에 이미 적용된 랜덤 이미지를 처리하는데 있어 번거로움이 발생한다.
        작성일: 2023.12.19
        작성자: yujin
        '''
        if profile_url is None:
            profile_url = f'https://api.dicebear.com/7.x/pixel-art/svg?seed=${phone}'

        hashed_password = make_password(password)

        user = User(
            phone=phone,
            password=hashed_password,
            nickname=nickname,
            profile_url=profile_url
        )
        user.save()

        return JsonResponse({
            "status": "success",
            "phone": phone,
            "nickname": nickname,
            "profile_url": profile_url,
            "message": "회원가입에 성공했습니다."
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "status": "success",
            "message": "회원가입에 실패했습니다."
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def send_auth_code(req):
    data = json.loads(req.body)
    phone = data.get('phone')

    timestamp = int(time.time() * 1000)
    timestamp = str(timestamp)

    url = "https://sens.apigw.ntruss.com"
    uri = f"/sms/v2/services/{settings.NCP_SENS_SERVICE_ID}/messages"

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
        "x-ncp-iam-access-key": settings.NCP_ACCESS_KEY,
        "x-ncp-apigw-signature-v2": generate_signature(
            settings.NCP_SECRET_KEY,
            settings.NCP_ACCESS_KEY,
            timestamp,
            url,
            uri
        )
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
        "from": settings.NCP_SENS_SEND_PHONE_NO,
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

