import base64
from io import BytesIO
import json
import cv2
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import FileSystemStorage

from user_auth.decorators import token_required
from .models import *
from django.core.files import File


from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime, timedelta
import requests
import os
from PIL import Image
from dotenv import load_dotenv

from ultralytics import YOLO


load_dotenv()
model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)

def index(req):
    if req.method == "GET":
        return JsonResponse({
            'status': 'success',
            'message': 'Shrink Django 서버가 정상적으로 실행중입니다.'
        }, status=200)
        
def find_first_friday(year, month, id):
        # 주어진 연도(year)와 월(month)로 해당 달의 1일 날짜를 만듭니다.
        date = datetime(year, month, 1)

        # 해당 달의 첫 번째 날부터 시작해서 금요일을 찾습니다.
        while date.weekday() != 4:  # 4는 금요일을 나타냅니다.
            date += timedelta(days=1)
        
        friday = date
        while True:
            temp = friday.strftime('%Y%m%d')
            PRICE_CHANGE_URL = f'http://openapi.price.go.kr/openApiImpl/ProductPriceInfoService/getProductPriceInfoSvc.do?serviceKey=elev%2BDdYEgCEiwXL1dcW5YyHQUrNmLOmCOsXZtLpyXOkaMQWobvID%2FLeqZAwouKbFDqLyzlqi8LvTN%2BTdAH3YA%3D%3D&goodInspectDay={temp}&goodId={id}'
            price = requests.get(PRICE_CHANGE_URL)
            price = price.text
            soup = BeautifulSoup(price, 'xml')
            print(soup)
            good_price_vo_exists = soup.find('iros.openapi.service.vo.goodPriceVO')
            if not good_price_vo_exists:
                friday = friday + timedelta(days=7)
            else:
                return friday.strftime('%Y%m%d'), soup
            
def select (req):

    PRODUCT_URL = f'http://openapi.price.go.kr/openApiImpl/ProductPriceInfoService/getProductInfoSvc.do?serviceKey=elev%2BDdYEgCEiwXL1dcW5YyHQUrNmLOmCOsXZtLpyXOkaMQWobvID%2FLeqZAwouKbFDqLyzlqi8LvTN%2BTdAH3YA%3D%3D&'
    response = requests.get(PRODUCT_URL)
    # print(response.text)
    xml = response.text
    text = BeautifulSoup(xml, 'xml')    

    items = text.find_all('item')
    # print(response.content)
    # response = response.json()
    result = {}
    for item in items:
        # <item>
        #     <goodId>1420</goodId>
        #     <goodName>하리보 골드베렌 젤리(250g)</goodName>
        #     <productEntpCode>2136</productEntpCode>
        #     <goodUnitDivCode>G</goodUnitDivCode>
        #     <goodBaseCnt>10</goodBaseCnt>
        #     <goodSmlclsCode>030205014</goodSmlclsCode>
        #     <detailMean>12g*21개</detailMean>
        #     <goodTotalCnt>250</goodTotalCnt>
        #     <goodTotalDivCode>G</goodTotalDivCode>
        # </item>
        good_id = item.find('goodId').text
        good_name = item.find('goodName').text
        key = good_name.split('(')[0]
        key = key.replace(' ','')
        detail_mean = item.find('detailMean').text if item.find('detailMean') is not None else None
        good_total_cnt = item.find('goodTotalCnt').text if item.find('goodTotalCnt') is not None else None
        result[key] = {'id': good_id, 'name':good_name, 'mean': detail_mean, 'cnt':good_total_cnt}
    
    find = req.GET.get('key')
    period = int(req.GET.get('period'))
    
    id = result[find]['id']
    print(id)
    print(datetime.today().month)
    
    current_year = datetime.today().year
    current_month = datetime.today().month  # 1은 1월을 나타냅니다.
    priceChange = []
    for _ in range(period):
        if current_month == 1:
            previous_month = 12
            previous_year = current_year - 1  # 연도도 조정해야 합니다.
        else:
            previous_month = current_month - 1
            previous_year = current_year

        inspectDay, soup = find_first_friday(current_year,current_month, id)
        # date_dict = {}
        prices = []
        for item in soup.find_all('iros.openapi.service.vo.goodPriceVO'):
            
            price = int(item.find('goodPrice').text)
            prices.append(price)
            # print( price)
        prices = np.array(prices)
        # print(round(prices.mean()))
        result_price = round(prices.mean())
        
        month_price= {
            'date': inspectDay,
            'price':result_price,
            '100Price':round((result_price/int(result[find]['cnt']))*100)
            }
        # print(month_price)
        
        priceChange.append(month_price)

        current_month = previous_month
        current_year = previous_year
        
    # result['pricechange'] = priceChgane
    priceChange.sort(key=lambda x:x['date'])
    
    productResult = {}
    # print(find)
    productResult[find] ={
        'id': id,
        'name': result[find]['name'],
        'mean': result[find]['mean'],
        'amount': result[find]['cnt'],
        'priceChange': priceChange
    }

    return JsonResponse(productResult)

@csrf_exempt
@require_http_methods(["POST"])
@token_required
def analysis(req):
    print(req)
    
    if req.method =='POST' and req.FILES['image']:        
        user = req.user

        image = req.FILES['image']
        fs = FileSystemStorage()
        if not os.path.exists('product/file'):
            os.makedirs('product/file')
        filename = fs.save('product/file/'+image.name, image)
        file_url = fs.url(filename)
        file_url = '.'+file_url
        

        results = model.predict(file_url,  save_txt=True)
        # os.remove(file_url)
        res_plotted = results[0].plot()
        print('-'*30, results[0])
        labels = results[0].names
        file_path = results[0].path
        save_dir = results[0].save_dir
        file_path = file_path.split('/')[-1].split('.')[0]+'.txt'
        # print(file_path)
        # print(save_dir+'\\'+file_path)
        file_path = save_dir+'/labels/'+file_path
        # file_path = os.path.join(save_dir, 'labels', file_path)
        print(file_path)
        file_path = file_path.replace('\\','/')
        print(file_path)
         

        try:
            with open(file_path, 'r') as file:
                for line in file:
                    # 공백을 기준으로 분할하여 첫 번째 값 가져오기
                    first_value = int(line.split()[0])
                    print(labels[first_value])  # 각 행의 첫 번째 값 출력

        except FileNotFoundError:
            print(f"파일 '{file_path}'을(를) 찾을 수 없습니다.")
        print(type(results[0]))
        image_data = np.array(res_plotted, dtype=np.uint8)
        # image = cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)  # 이미지 생성 (BGR 형식으로)
        # print(image_data)
        
        # image_data를 OpenCV로 다루고 PIL Image 객체로 변환 (RGB 형식)
        img = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img.astype('uint8'))

        # BytesIO에 이미지 저장
        image_io = BytesIO()
        img_pil.save(image_io, format='PNG')  # 이미지를 원하는 형식으로 저장(PNG, JPEG 등)
        image_io.seek(0)  # BytesIO의 파일 포인터를 처음으로 이동

        # ProductAnalysis 모델 객체 생성 및 이미지 저장
        if not os.path.exists('product/detect'):
            os.makedirs('product/detect')

        product_analysis = ProductAnalysis()
        product_analysis.user = user
        product_analysis.save()  # 데이터베이스에 모델 객체 저장

        # BytesIO를 Django의 File 객체로 변환하여 ImageField에 저장
        product_analysis.image.save('image.png', image_io, save=True)
        
        return JsonResponse({'response':product_analysis.id})
        
    return JsonResponse({'response':True})

def get_image(req, image_url):
    # 이미지가 저장된 모델에서 해당 이미지의 인스턴스를 가져옵니다.
    # return JsonResponse({'response':True})
    
    print(123123)
    image_instance = get_object_or_404(ProductAnalysis, pk=image_url)
    
    # 이미지 파일의 경로를 가져옵니다.
    image_path = image_instance.image.path
    print(image_path)
    # 이미지 파일을 읽어와 HTTP 응답으로 반환합니다.
    with open(image_path, 'rb') as f:
        return HttpResponse(f.read(), content_type='image/png')  # 이미지 타입에 따라 content_type 변경 가능
    

@csrf_exempt
@require_http_methods(["POST"])
def selectProduct(request):
    # print(1231213)
    if request.method == 'POST':
        # print(1231213)
        # data = json.loads(req.body)
        # content = data.get('content')
        data = json.loads(request.body)
        
        name_to_search = data.get('product_name')
        # period_to_search = data.get('period')
        print(name_to_search)
        try:
            products = Product.objects.filter(product_name__icontains=name_to_search)
            product_list = []
            for product in products:
                print(product.product_id)
                prices = PriceChange.objects.filter(product_id=product.product_id).order_by('date')
                print(prices)
                temp = list(prices.values())

                print(temp)  # 가격 변경 정보를 리스트로 출력
                # price_list.append({product.product_id:temp})
                product_info = {
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'product_detail': product.detail,
                    'product_weight': product.weight
                }
                price_dict = {
                    product.product_name: product_info,
                    'prices': temp
                }
                product_list.append(price_dict)

        except Product.DoesNotExist:
            products = None
    
    serialized_products = list(products.values())
    return JsonResponse({'response':product_list})



def test(req): ## 상품 api -> DB
    URL = 'http://openapi.price.go.kr/openApiImpl/ProductPriceInfoService/getProductInfoSvc.do?serviceKey=elev%2BDdYEgCEiwXL1dcW5YyHQUrNmLOmCOsXZtLpyXOkaMQWobvID%2FLeqZAwouKbFDqLyzlqi8LvTN%2BTdAH3YA%3D%3D&'
    response = requests.get(URL)
    # print(response.text)
    xml = response.text
    text = BeautifulSoup(xml, 'xml')    

    items = text.find_all('item')
    # result = set()
    result = []
    for item in items:
        
        good_id = item.find('goodId').text
        # result.add(good_id)
        good_name = item.find('goodName').text.replace(' ','')        
        detail_mean = item.find('detailMean').text if item.find('detailMean') is not None else None
        weight = item.find('goodTotalCnt').text if item.find('goodTotalCnt') is not None else None
        # Product 모델에 데이터 저장
        product = Product(
            product_id=good_id,
            product_name=good_name,
            detail=detail_mean,
            weight=weight,
        )
        print(product.product_id)
        product.save()  # 데이터베이스에 저장

                

    return JsonResponse({'response': True})


def find_first_friday():
    date = datetime.now()
    print(date.year, date.month, date.day)
    date = datetime(date.year, date.month, date.day)
    while True:
        temp = date.strftime('%Y%m%d')

        PRICE_CHANGE_URL = f'http://openapi.price.go.kr/openApiImpl/ProductPriceInfoService/getProductPriceInfoSvc.do?serviceKey=elev%2BDdYEgCEiwXL1dcW5YyHQUrNmLOmCOsXZtLpyXOkaMQWobvID%2FLeqZAwouKbFDqLyzlqi8LvTN%2BTdAH3YA%3D%3D&goodInspectDay={temp}&goodId=1182'
        price_change = requests.get(PRICE_CHANGE_URL).text
        soup = BeautifulSoup(price_change, 'xml')
        good_price_vo_exists = soup.find('iros.openapi.service.vo.goodPriceVO')
        if not good_price_vo_exists:
            date = date - timedelta(days=1)
        else:
            print(date)
            return date
    

def test2(req): # 상품정보로 가격정보 저장
    products = Product.objects.all()
    print(len(products))
    result = []
    # print(find_first_friday())
    date = find_first_friday()
    # date = datetime(23, 12, 22)
    # date = date.strftime('%Y%m%d')
    while True:
        
        temp = date.strftime('%Y%m%d')
        formatted_date = datetime.strptime(temp, '%Y%m%d').date()
        for product in products:
            print(product.product_id, product.product_name)
            result = PriceChange.objects.filter(product_id=product.product_id, date=formatted_date)
            # 결과가 있는 경우에만 continue
            if result.exists():
                continue

            try:
                PRICE_CHANGE_URL = f'http://openapi.price.go.kr/openApiImpl/ProductPriceInfoService/getProductPriceInfoSvc.do?serviceKey=elev%2BDdYEgCEiwXL1dcW5YyHQUrNmLOmCOsXZtLpyXOkaMQWobvID%2FLeqZAwouKbFDqLyzlqi8LvTN%2BTdAH3YA%3D%3D&goodInspectDay={temp}&goodId={product.product_id}'
                price_change = requests.get(PRICE_CHANGE_URL).text
                # price_change.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"요청 중 오류 발생: {e}")
            # print(price_change)
            soup = BeautifulSoup(price_change, 'xml')
            # print(soup)
            max_price = 0
            min_price = float('inf')
            # date = '20231222'
            mean_price = 0
            count = 0
            good_price_vo_exists = soup.find('iros.openapi.service.vo.goodPriceVO')
            if not good_price_vo_exists:
                print('-'*30, 'continue')
                continue
            for item in soup.find_all('iros.openapi.service.vo.goodPriceVO'):
                price = int(item.find('goodPrice').text)
                mean_price += price
                count+=1
                max_price = max(max_price, price)
                min_price = min(min_price, price)
                # print(price)
            # print(count)
            try: 
                mean_price = mean_price//count
                print(max_price, min_price, mean_price)
                # result.append((max_price, min_price, mean_price))
            except ZeroDivisionError:
                # result.append(None)
                mean_price = None
                max_price = None
                min_price = None
                print(None)
            # break
            print('-'*30,date)
            price_change = PriceChange(
                product = product,
                date = date,
                price = mean_price,
                max_price = max_price,
                min_price = min_price
            )
            price_change.save()
        date = date - timedelta(days=14)
        if date<datetime(2018,8,31):
            break
        
        
        
    return JsonResponse({'response': True})


def yolotest(req):

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("웹캠이 정상적으로 열리지 않았습니다. 확인해주세요.")
        return
    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()
        if not success:
            print("프레임을 읽을 수 없습니다.")
            break
        if success:
            # Run YOLOv8 inference on the frame
            results = model(frame)

            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            # Display the annotated frame
            cv2.imshow("YOLOv8 Inference", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' 키를 누르면 종료
            break



def stream_video(request):
    cap = cv2.VideoCapture(0)

    def generate_frames():
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                # Run YOLOv8 inference on the frame
                results = model(frame)

                # Visualize the results on the frame
                annotated_frame = results[0].plot()
                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')
