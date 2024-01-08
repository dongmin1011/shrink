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
from django.core.paginator import Paginator
from django.db.models import Count


from .models import Like, Report, ReportImage, ShrinkFlationGeneration
from product.models import Product
from django.utils import timezone
from PIL import Image, ExifTags
from io import BytesIO


def image_return_url(url):
    return "https://api.dietshrink.kro.kr/api/report/select/image/"+url

@csrf_exempt
@require_http_methods(["POST"])
@token_required
def write_report(req):
    existing_user = req.user
    print(existing_user)
    # if existing_user.is_anonymous:
    #     return JsonResponse({
    #         'status': 'fail',
    #         'message':'사용자 정보 없음'
    #     })
    
    uploaded_images = req.FILES.getlist('image')  # 여러 사진을 가져오기  # 파일 가져오기
    json_data = json.loads(req.POST['data'])  # JSON 데이터 가져오기

    product = json_data.get('product')
    product_name = json_data.get('product_name')
    weight = json_data.get('weight')
    price = int(json_data.get('price'))
    content = json_data.get('content')
    unit = json_data.get('unit')
        
    print(unit)
    
    # existing_user = User.objects.get(phone='01066594660')
    product = Product.objects.get(product_id = product)
    report = Report.objects.create(
        user=existing_user,  # 위에서 가져온 기존 User 객체를 연결합니다
        created_at=timezone.now(),
        price=price,
        product=product,
        product_name = product_name,
        weight = weight,
        content = content,
        unit = unit,
        status = 1,
        
    )
    # file_urls = []
    print("--", uploaded_images)
    for image in uploaded_images:
            # 이미지를 메모리에 로드
        img = Image.open(image)
        print(img)
        # if img.mode == 'RGBA':
        #     img = img.convert('RGB')
        # 이미지 형식이 jpg일 때만 EXIF 데이터 확인
        print(img.format)
        print(img.getexif)
        if img.format == 'JPEG'  and hasattr(img, '_getexif'):
            exif = img._getexif()
            print("jpg"*10)

            if exif is not None:
                exif = dict(exif)
                orientation_key = [key for key, value in ExifTags.TAGS.items() if value == 'Orientation']
                orientation = exif.get(orientation_key[0], None) if orientation_key else None

                # 이미지 회전
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
                    
            width, height = img.size
            # 이미지 리사이징
            resized_img = img.resize((width//2, height//2))

            
            buffer = BytesIO()
            resized_img.save(buffer, format='JPEG', quality=60)

            # 저장된 이미지를 ReportImage에 저장
            report_image = ReportImage(report=report)
            report_image.image.save('image.jpg', File(buffer), save=True)
        # elif img.format == 'MPO':
            
        #     selected_frame = img.copy()  # 선택한 프레임 복사
            
        #     selected_frame = Image.Image._new(selected_frame)

            
        #     exif = selected_frame._getexif()
        #     if exif is not None:
        #         exif = dict(exif)
        #         orientation_key = [key for key, value in ExifTags.TAGS.items() if value == 'Orientation']
        #         orientation = exif.get(orientation_key[0], None) if orientation_key else None

        #         # 이미지 회전에 따른 resize 작업
        #         if orientation in [3, 6, 8]:
        #             # 회전된 경우, 먼저 이미지를 회전시킨 후 resize
        #             if orientation == 3:
        #                 selected_frame = selected_frame.rotate(180, expand=True)
        #             elif orientation == 6:
        #                 selected_frame = selected_frame.rotate(270, expand=True)
        #             elif orientation == 8:
        #                 selected_frame = selected_frame.rotate(90, expand=True)
        #         width, height = img.size
        #         # 이미지 리사이징
        #         resized_img = img.resize((width//2, height//2))

                
        #         buffer = BytesIO()
        #         resized_img.save(buffer, format='png', quality=60)

        #         # 저장된 이미지를 ReportImage에 저장
        #         report_image = ReportImage(report=report)
        #         report_image.image.save('image.png', File(buffer), save=True)
        else:
            width, height = img.size
            # 이미지 리사이징
            resized_img = img.resize((width//2, height//2))

            
            buffer = BytesIO()
            resized_img.save(buffer, format='png', quality=60)

            # 저장된 이미지를 ReportImage에 저장
            report_image = ReportImage(report=report)
            report_image.image.save('image.png', File(buffer), save=True)
        print(report_image.image.path)
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
    user = req.user if req.user else None
    print(user)
    
    # Report 모델의 모든 객체 조회
    all_reports = Report.objects.all().order_by('-created_at').values()
    
    # page_number = req.GET.get('page', 1)
    items_per_page = req.GET.get('per_page', 5)
    
    paginator = Paginator(all_reports, items_per_page)
    
    
    page_obj = paginator.page(1)
    
    result =[]
    for report in page_obj:
        print(report['id'])
        user = User.objects.get(id=report['user_id'])
        like_count = Like.objects.filter(report=report['id']).count()  ##report의 좋아요 개수 가지고 오기

        # print(user)
        
        report['user_id']=None
        report['user_name'] = user.nickname
        report['profile_url'] = user.profile_url
        
        status_display = dict(Report.STATUS_CHOICES).get(report['status'])
        # print("123", status_display)
        report['status'] = status_display
        report_image = ReportImage.objects.filter(report=report['id']).values('id')
        # print(list(report_image))
        report_image = list(report_image)
        for i in range(len(report_image)):
            report_image[i]['id'] = image_return_url(str(report_image[i]['id']))
            
        report['like'] = like_count
        
        if report_image:
            report['thumbnail'] = report_image[0]['id']
        else:
            report['thumbnail'] = None
        report['images'] = report_image
        result.append(report)
        
    # all_reports = list(all_reports)
    # print(all_reports)
    return JsonResponse({
        'status':'success',
        'response':result
    })
#로그인한 사용자가 좋아요를 눌렀는지 확인
@token_required
def is_like(req, query_id):
    user = req.user
    report =  get_object_or_404(Report, pk=query_id)
    print(report)
    try:
        likes = Like.objects.get(user=user, report=report)
        print(likes)
        return JsonResponse({"status":"success", "response":True})
    except:
        return JsonResponse({"status":"success", "response":False})
    

#로그인한 사용자가 작성한 게시물인지 확인
@token_required
def is_your_report(req, query_id):
    user = req.user
    report =  get_object_or_404(Report, pk=query_id)
    
    if report.user == user:
        return JsonResponse({"status":"success", "response":True})
    else:
        return JsonResponse({"status":"success", "response":False})

#로그인한 사용자가 좋아요를 누른 모든 게시물 반환
@token_required
def user_like_all(req):
    user= req.user
    user_like_list=[]
    try:
        # reports = Report.objects.all()
        # print(user)
        # print(Like.objects.all().values('user'))
        likes = Like.objects.filter(user=user)
        # print(likes)
        for like in likes:
            # print(like)
            user_like_list.append(like.report.id)
        
        # for report in reports:
        #     print(report.id)
        #     try:
        #         likes = Like.objects.get(user=user, report=report)
        #         print(likes)
        #         user_like_list.append(report.id)
        #         print(user_like_list)
        #     except:
        #         continue
        return JsonResponse({"status":'success', "like_list":user_like_list})
    except:
        return JsonResponse({"status":'fail', "response":False, "message":"좋아요 리스트가 없습니다."})

#신고내역 상세 페이지
def select_detail(req, query_id):
    try:
        report = Report.objects.get(id=query_id)
        print(report)
        report_image = ReportImage.objects.filter(report=report.id).values('id')
        print(report.user_id)
        user = User.objects.get(id=report.user_id)
        
        like_count = Like.objects.filter(report=report).count()  ##report의 좋아요 개수 가지고 오기
        print(like_count)
        

        status_display = dict(Report.STATUS_CHOICES).get(report.status)

        # report['status'] = status_display
        report_image = list(report_image)
        for i in range(len(report_image)):
            report_image[i]['id'] = image_return_url(str(report_image[i]['id']))
        report_values = {
            "id": report.id,
            "product_name": report.product_name,
            "price": report.price,
            "weight": report.weight,
            "created_at": report.created_at,
            "content": report.content,
            "status": status_display,
            "user_name": report.user.nickname,
            'profile_url' : user.profile_url,
            'likes' : like_count,
            "images": list(report_image)
        }
        return JsonResponse({
            'status':'success',
            'response':report_values
        })
    except Exception as e:
        print(e)
        return JsonResponse({
            'status':'fail',
            'response': None
        })
#슈링크플레이션 발생 상품 추가
@csrf_exempt
@require_http_methods(["POST"])
def create_shrink(req):
    data = json.loads(req.body)
    product = data.get('product', None)
    report = data.get('report', None)
    before = data.get('before', None)
    after = data.get('after', None)
    
    try:
        shrink = ShrinkFlationGeneration()
        
        if report:
            report = Report.objects.get(id = report)
            after= report.weight
        if product:
            product = Product.objects.get(product_id = product)
            before = product.weight
        
        
        shrink.report = report
        shrink.product = product
        shrink.before = before
        shrink.after = after
        
        shrink.save()
        return JsonResponse({'status':"success"})
    except Exception as e: #이미 슈링크 발생한 제품 업데이트
        shrink = ShrinkFlationGeneration.objects.get(product_id = product)
        if report:
            report = Report.objects.get(id = report)
            after= report.weight
        
        shrink.report = report
        
        shrink.before = before
        shrink.after = after
        
        shrink.save()
        return JsonResponse({'status':"success", "response": str(e)})

#슈링크플레이션 발생 상품 삭제
@csrf_exempt
@require_http_methods(["DELETE"])   
def delete_shrink(req):
    try:
        data = json.loads(req.body)
        product = data.get('product', None)
        report = data.get('report', None)
        
        if report:
            report = Report.objects.get(id=report)
            ShrinkFlationGeneration.objects.get(report=report).delete()
        elif product:
            product = Product.objects.get(product_id=product)
            ShrinkFlationGeneration.objects.get(product=product).delete()
        
        
        
        return JsonResponse({'status':"success"})
    except Exception as e :
        return JsonResponse({'status':"fail", "message":str(e)})

#슈링크플레이션 발생 상품 조회
@csrf_exempt
@require_http_methods(["GET"])
def select_shrink(req):
    try:
        shrink = ShrinkFlationGeneration.objects.all().values()
    
        return JsonResponse({'status':"success", 'response': list(shrink)})
    except:
        return JsonResponse({'status':"fail"})
        

# 신고 좋아요
@require_http_methods(["POST"])
@csrf_exempt
@token_required
def like_report(req, query_id):
    try:
        report = get_object_or_404(Report, id=query_id)
        user = req.user

        like, created = Like.objects.get_or_create(report=report, user=user)
        
        if not created:
            like.delete()
            return JsonResponse({
                'status': 'success',
                'message': f'{query_id}번 게시물의 좋아요가 제거되었습니다.'
            })
        return JsonResponse({
            'status': 'success',
            'message': f'{query_id}번 게시물의 좋아요가 추가되었습니다.'
        })
    except Report.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '해당 게시물을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'좋아요 처리 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


## 제품 이름 입력시 신고된 내용이 있는지 출력 - 만약 신고내용이 없다면 {response:null}
@csrf_exempt
@require_http_methods(["POST"])
def select(req):
    data = json.loads(req.body)
    product = data.get('product')
    items_per_page = data.get('per_page', 10)
    
    desired_product_reports = Report.objects.filter(product_name__icontains=product).order_by('-created_at').values()
    
    paginator = Paginator(desired_product_reports, items_per_page)
    
    
    page_obj = paginator.page(1)
    
    result = []
    for report in page_obj:
        
        user = User.objects.get(id=report['user_id'])
        print(user)
        like_count = Like.objects.filter(report=report['id']).count()  ##report의 좋아요 개수 가지고 오기

        
        report['user_id']=None
        report['user_name'] = user.nickname
        report['profile_url'] = user.profile_url

        
        status_display = dict(Report.STATUS_CHOICES).get(report['status'])
        # print("123", status_display)
        report['status'] = status_display
        report_image = ReportImage.objects.filter(report=report['id']).values('id')
        report_image = list(report_image)
        report['like'] = like_count
        for i in range(len(report_image)):
            report_image[i]['id'] = image_return_url(str(report_image[i]['id']))
        
        if report_image:
            report['thumbnail'] = report_image[0]['id']
        else:
            report['thumbnail'] = None
        report['images'] = report_image
        result.append(report)
        
    # reports_list = list(desired_product_reports)  # QuerySet을 리스트로 변환
    if result:
        return JsonResponse({'status':'success', "response":result})
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
    desired_product_reports = Report.objects.filter(user=existing_user).order_by('-created_at').values()
    data = json.loads(req.body)
    items_per_page = data.get('per_page', 10)
    paginator = Paginator(desired_product_reports, items_per_page)
    page_obj = paginator.page(1)
    
    result = []
    for report in page_obj:
        
        user = User.objects.get(id=report['user_id'])
        print(user)
        like_count = Like.objects.filter(report=report['id']).count()  ##report의 좋아요 개수 가지고 오기

        
        report['user_id']=None
        report['user_name'] = user.nickname
        report['profile_url'] = user.profile_url

        
        status_display = dict(Report.STATUS_CHOICES).get(report['status'])
        # print("123", status_display)
        report['status'] = status_display
        report_image = ReportImage.objects.filter(report=report['id']).values('id')
        report_image = list(report_image)
        report['like'] = like_count
        
        for i in range(len(report_image)):
            report_image[i]['id'] = image_return_url(str(report_image[i]['id']))
        if report_image:
            report['thumbnail'] = report_image[0]['id']
        else:
            report['thumbnail'] = None
        report['images'] = report_image
        result.append(report)
        
    # reports_list = list(desired_product_reports)  # QuerySet을 리스트로 변환
    if result:
        return JsonResponse({'status':'success', "response":result})
    else:
        return JsonResponse({'status':'fail',"response":None})
    
#신고내용 삭제
@require_http_methods(["DELETE"])
@csrf_exempt
@token_required
def delete_report(req, query_id):
    # print
    try:
        report = get_object_or_404(Report, id=query_id)
        if report.user != req.user:
            return JsonResponse({
                'status': 'fail',
                'message': '게시물 삭제 권한이 없습니다.'
            }, status=403)
        for report_image in report.reportimage_set.all():
                image_path = report_image.image.path  # image_field는 실제 이미지를 담는 필드명입니다.
                print(image_path)
                # 파일 삭제
                if os.path.exists(image_path):
                    os.remove(image_path)
        report.reportimage_set.all().delete()  # 기존 이미지 삭제

        report.delete()
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
        

# 신고내역 수정 - 사용자용
@require_http_methods(["POST"])
@csrf_exempt
@token_required
def update_report(req, query_id):
    try:
        report = get_object_or_404(Report, id=query_id)
        if report.user != req.user:
            return JsonResponse({
                'status': 'fail',
                'message': '게시물 수정 권한이 없습니다.'
            }, status=403)
        # print(report)
        # data = json.loads(req.body)
        # queryboard.title = data.get('title', queryboard.title)
        # queryboard.content = data.get('content', queryboard.content)
        # queryboard.save()
        update_images = req.FILES.getlist('image')  # 여러 사진을 가져오기  # 파일 가져오기
        # print(update_images)

        # json_data = json.loads(req.body)  # JSON 데이터 가져오기
        json_data = json.loads(req.POST['data'])
        print(json_data)
        report.product_name = json_data.get('product', report.product_name)
        report.weight = json_data.get('weight', report.weight)
        report.price = int(json_data.get('price', report.price))
        report.content = json_data.get('content', report.content)
        report.unit = json_data.get('unit', report.unit)

        # 이미지 필드 업데이트
        if update_images:
            # 업로드된 이미지가 있을 경우
            for report_image in report.reportimage_set.all():
                image_path = report_image.image.path  # image_field는 실제 이미지를 담는 필드명입니다.
                print(image_path)
                # 파일 삭제
                if os.path.exists(image_path):
                    os.remove(image_path)
            report.reportimage_set.all().delete()  # 기존 이미지 삭제

            for image in update_images:
            # 이미지를 메모리에 로드
                img = Image.open(image)
                print(img)
                
                # 이미지 형식이 jpg일 때만 EXIF 데이터 확인
                if img.format == 'JPEG' and hasattr(img, '_getexif'):
                    exif = img._getexif()

                    if exif is not None:
                        exif = dict(exif)
                        orientation_key = [key for key, value in ExifTags.TAGS.items() if value == 'Orientation']
                        orientation = exif.get(orientation_key[0], None) if orientation_key else None

                        # 이미지 회전
                        if orientation == 3:
                            img = img.rotate(180, expand=True)
                        elif orientation == 6:
                            img = img.rotate(270, expand=True)
                        elif orientation == 8:
                            img = img.rotate(90, expand=True)
                            
                    width, height = img.size
                    # 이미지 리사이징
                    resized_img = img.resize((width//2, height//2))

                    
                    buffer = BytesIO()
                    resized_img.save(buffer, format='JPEG', quality=60)

                    # 저장된 이미지를 ReportImage에 저장
                    report_image = ReportImage(report=report)
                    report_image.image.save('image.jpg', File(buffer), save=True)
                else:
                    width, height = img.size
                    # 이미지 리사이징
                    resized_img = img.resize((width//2, height//2))

                    
                    buffer = BytesIO()
                    resized_img.save(buffer, format='png', quality=60)

                    # 저장된 이미지를 ReportImage에 저장
                    report_image = ReportImage(report=report)
                    report_image.image.save('image.png', File(buffer), save=True)

        report.save()  # 변경된 필드들 저장

        return JsonResponse({
            'status': 'success',
            'message': f'{report.id}번 게시물이 성공적으로 수정되었습니다.'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'fail',
            'message': '잘못된 형식의 데이터입니다.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'게시물 수정 중 오류가 발생했습니다: {str(e)}'
        }, status=500)