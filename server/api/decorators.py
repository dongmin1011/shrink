import jwt
from django.http import JsonResponse
from django.conf import settings
from functools import wraps
from .models import User

def token_required(f):
    @wraps(f)
    def decorated(request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')

        if not token or not token.startswith('Bearer '):
            return JsonResponse({
                'status': 'fail',
                'message': '토큰이 존재하지 않습니다.'
            }, status=401)

        try:
            token = token.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            request.user = user
        except (jwt.DecodeError, jwt.ExpiredSignatureError, User.DoesNotExist):
            return JsonResponse({
                'status': 'fail',
                'message': '유효하지 않은 토큰입니다.'
            }, status=401)

        return f(request, *args, **kwargs)
    return decorated
