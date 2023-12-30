from io import BytesIO
import json
import mimetypes
import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from user_auth.models import User
from user_auth.decorators import token_required
from django.core.files.storage import FileSystemStorage
from django.core.files import File


from .models import Report, ReportImage
from django.utils import timezone


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def write_report(req):
    existing_user = req.user
    if existing_user.is_anonymous:
        return JsonResponse({
            'status': 'fail',
            'message':'사용자 정보 없음'
        })
    
    uploaded_images = req.FILES.getlist('image')  # 여러 사진을 가져오기  # 파일 가져오기
    json_data = json.loads(req.POST['data'])  # JSON 데이터 가져오기

    product = json_data.get('product')
    weight = json_data.get('weight')
    price = int(json_data.get('price'))
    content = json_data.get('content')

        
    
    
    # existing_user = User.objects.get(phone='01066594660')
    report = Report.objects.create(
        user=existing_user,  # 위에서 가져온 기존 User 객체를 연결합니다
        created_at=timezone.now(),
        price=price,
        product_name=product,
        weight = weight,
        content = content,
        status = 1,
        
    )
    # file_urls = []
    
    for image in uploaded_images:
        report_images = ReportImage(report=report)
        report_images.image.save('image.png', File(image), save=True)

    return JsonResponse({
        "status": "success",
        "message": "신고가 접수되었습니다."
    }, status=200)

def get_image(req, image_url):
    # 이미지가 저장된 모델에서 해당 이미지의 인스턴스를 가져옵니다.
    # return JsonResponse({'response':True})
    
    print(123123)
    image_instance = get_object_or_404(ReportImage, pk=image_url)
    
    # 이미지 파일의 경로를 가져옵니다.
    image_path = image_instance.image.path
    print(image_path)
    # 이미지 파일을 읽어와 HTTP 응답으로 반환합니다.
    with open(image_path, 'rb') as f:
        content_type, _ = mimetypes.guess_type(image_path)
        if not content_type:  # MIME 타입을 추측할 수 없는 경우
            content_type = 'image/png'  # 기본적으로 png 이미지로 처리

        return HttpResponse(f.read(), content_type=content_type)


## 신고된 제품 전체 출력
def selectALL(req):
    # Report 모델의 모든 객체 조회
    all_reports = Report.objects.all().values()
    for report in all_reports:
        user = User.objects.get(id=report['user_id'])
        print(user)
        
        report['user_id']=None
        report['user_name'] = user.nickname
        
        status_display = dict(Report.STATUS_CHOICES).get(report['status'])
        # print("123", status_display)
        report['status'] = status_display
        report_image = ReportImage.objects.filter(report=report['id']).values('id')
        print(list(report_image))
        report['images'] = list(report_image)
        
    all_reports = list(all_reports)
    # print(all_reports)
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
    
    desired_product_reports = Report.objects.filter(product_name__icontains=product).values( )
    for report in desired_product_reports:
        
        user = User.objects.get(id=report['user_id'])
        print(user)
        
        report['user_id']=None
        report['user_name'] = user.nickname
        
        
        status_display = dict(Report.STATUS_CHOICES).get(report['status'])
        # print("123", status_display)
        report['status'] = status_display
        report_image = ReportImage.objects.filter(report=report['id']).values('id')
        print(list(report_image))
        report['images'] = list(report_image)
        
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
    except:
        return JsonResponse({
            'status': 'fail',
            'message':'사용자 정보 없음'
        })
    desired_product_reports = Report.objects.filter(user=existing_user).values()
    for report in desired_product_reports:
        
        user = User.objects.get(id=report['user_id'])
        print(user)
        
        report['user_id']=None
        report['user_name'] = user.nickname
        
        
        status_display = dict(Report.STATUS_CHOICES).get(report['status'])
        # print("123", status_display)
        report['status'] = status_display
        report_image = ReportImage.objects.filter(report=report['id']).values('id')
        print(list(report_image))
        report['images'] = list(report_image)
        
    reports_list = list(desired_product_reports)  # QuerySet을 리스트로 변환
    if reports_list:
        return JsonResponse({'status':'success', "response":reports_list})
    else:
        return JsonResponse({'status':'fail',"response":None})
    
#신고내용 삭제
@require_http_methods(["DELETE"])
@csrf_exempt
@token_required
def delete_report(req, query_id):
    # print
    try:
        queryboard = get_object_or_404(Report, id=query_id)
        if queryboard.user != req.user:
            return JsonResponse({
                'status': 'fail',
                'message': '게시물 삭제 권한이 없습니다.'
            }, status=403)

        queryboard.delete()
        return JsonResponse({
            'status': 'success',
            'message': f'{query_id}번 게시물이 성공적으로 삭제되었습니다.'
        })
    except Report.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '해당 게시물을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'게시물 삭제 중 오류가 발생했습니다: {str(e)}'
        }, status=500)