from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


def index(req):
    if req.method == "GET":
        return JsonResponse({
            'status': 'success',
            'message': 'Shrink Django 서버가 정상적으로 실행중입니다.'
        }, status=200)


'''
    설명: Redis 캐시에 키-값을 저장하고 조회하는 API 입니다. 테스트용으로 사용하며 현재는 사용하지 않아 주석처리합니다.
    작성일: 2023.12.20
    작성자: yujin

@csrf_exempt
@require_http_methods(["POST"])
def set_value(req):
    try:
        data = json.loads(req.body)
        key = data.get('key')
        value = data.get('value')

        cache.set(key, value, timeout = 30)

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
'''