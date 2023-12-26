import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from user_auth.models import User
from user_auth.decorators import token_required

from .models import Report
from django.utils import timezone


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def write_report(req):
    data = json.loads(req.body)
    product = data.get('product')
    weight = data.get('weight')
    price = int(data.get('price'))
    content = data.get('content')
    
    
    print('product, weight >> ', product, weight)
    print('req user >> ', req.user)
    print('req user >> ', req.user.id)
    
    # existing_user = req.user
    # if existing_user.is_anonymous:
    #     return JsonResponse({
    #         'status': 'fail',
    #         'message':'사용자 정보 없음'
    #     })
    
    existing_user = User.objects.get(phone='01066594660')
    report = Report.objects.create(
        user=existing_user,  # 위에서 가져온 기존 User 객체를 연결합니다
        created_at=timezone.now(),
        price=price,
        product_name=product,
        weight = weight,
        content = content,
        status = 1,
        
    )
    return JsonResponse({
        "status": "success",
        "message": "신고가 접수되었습니다."
    }, status=200)

## 신고된 제품 전체 출력
def selectALL(req):
    # Report 모델의 모든 객체 조회
    all_reports = Report.objects.all().values()
    for report in all_reports:
        status_display = dict(Report.STATUS_CHOICES).get(report['status'])
        # print("123", status_display)
        report['status'] = status_display

    all_reports = list(all_reports)
    print(all_reports)
    return JsonResponse({
        'status':'success',
        'response':all_reports
    })

## 제품 이름 입력시 신고된 내용이 있는지 출력 - 만약 신고내용이 없다면 {response:null}
@csrf_exempt
@require_http_methods(["POST"])
def select(req):
    data = json.loads(req.body)
    product = data.get('product')
    
    desired_product_reports = Report.objects.filter(product_name=product).values( )
    for report in desired_product_reports:
        status_display = dict(Report.STATUS_CHOICES).get(report['status'])
        # print("123", status_display)
        report['status'] = status_display
    reports_list = list(desired_product_reports)  # QuerySet을 리스트로 변환
    if reports_list:
        return JsonResponse({'status':'success', "response":reports_list})
    else:
        return JsonResponse({'status':'fail',"response":None})

## 사용자가 자신이 신고한 내용을 확인할 때 사용
@csrf_exempt
@require_http_methods(["POST"])
@token_required
def selectUser(req):
    
    try:
        existing_user = req.user
        # existing_user = User.objects.get(phone='01066594660')
    except:
        return JsonResponse({
            'status': 'fail',
            'message':'사용자 정보 없음'
        })
    desired_product_reports = Report.objects.filter(user=existing_user).values()
    for report in desired_product_reports:
        status_display = dict(Report.STATUS_CHOICES).get(report['status'])
        # print("123", status_display)
        report['status'] = status_display
    reports_list = list(desired_product_reports)  # QuerySet을 리스트로 변환
    if reports_list:
        return JsonResponse({'status':'success', "response":reports_list})
    else:
        return JsonResponse({'status':'fail',"response":None})