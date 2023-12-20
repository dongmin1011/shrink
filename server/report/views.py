from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from user_auth.decorators import token_required

@csrf_exempt
@require_http_methods(["POST"])
@token_required
def write_report(req):
    data = json.loads(req.body)
    product = data.get('product')
    content = data.get('content')

    print('product, content >> ', product, content)
    print('req user >> ', req.user)
    print('req user >> ', req.user.id)

    return JsonResponse({
        "status": "success",
        "message": "신고가 접수되었습니다."
    }, status=200)

