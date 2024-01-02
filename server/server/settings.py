
from pathlib import Path

import os
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-v20wnaxwb-e)wqt%u1gq_(us599zaap*+txx-*kp-l=(+8il$0"


NCP_ACCESS_KEY = os.getenv('NCP_ACCESS_KEY')
NCP_SECRET_KEY = os.getenv('NCP_SECRET_KEY')
NCP_SENS_SERVICE_ID = os.getenv('NCP_SENS_SERVICE_ID')
NCP_SENS_SEND_PHONE_NO = os.getenv('NCP_SENS_SEND_PHONE_NO')

AWS_S3_ACCESS_KEY_ID = os.getenv('AWS_S3_ACCESS_KEY_ID')
AWS_S3_SECRET_ACCESS_KEY = os.getenv('AWS_S3_SECRET_ACCESS_KEY')
AWS_S3_STORAGE_BUCKET_NAME = os.getenv('AWS_S3_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')

DEBUG = True

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    # 'drf_yasg', # Swagger API 문서 생성 라이브러리(사용법 복잡해서 보류) 23.12.21 yujin
    "user_auth",
    "favorite",
    "product",
    "report",
    'query',
    "alert",
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


CORS_ALLOW_CREDENTIALS = True  # True 상태면 HTTP 상태에서도 쿠키를 요청에 포함

CORS_ORIGIN_ALLOW_ALL = True  # 모든 도메인에 대해 허용
CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://localhost:3000',
    'https://127.0.0.1:3000',
    'https://www.dietshrink.site',
)

CSRF_TRUSTED_ORIGINS = (
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://localhost:3000',
    'https://127.0.0.1:3000',
    'https://www.dietshrink.site',
)


ROOT_URLCONF = "server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "server.wsgi.application"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('AWS_RDS_MYSQL_DB_NAME'),
        'USER': os.getenv('AWS_RDS_MYSQL_USER_NAME'),
        'PASSWORD': os.getenv('AWS_RDS_MYSQL_PASSWORD'),
        'HOST': os.getenv('AWS_RDS_MYSQL_HOST'),
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET time_zone='+09:00'",
        },
    },
    'mongodb': {
        'ENGINE': 'djongo',
        'NAME': os.getenv('MONGO_NAME'),
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': os.getenv('MONGO_HOST'),
        }
    }
}


REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_INDEX = os.getenv('REDIS_INDEX')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_INDEX}]",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",

        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]



LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

# (24.01.02 사용안함)Local 서버 시간을 사용해 DB에 저장하기 위해 False로 변경(한국시간) 23.12.27 yujin
# UTC 시간대 사용
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

 
