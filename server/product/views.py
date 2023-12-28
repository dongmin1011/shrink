import base64
from io import BytesIO
import cv2
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import FileSystemStorage
from .models import ProductAnalysis
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
# @require_http_methods(["POST"])
def analysis(req):
    print(req)
    if req.method =='POST' and req.FILES['image']:
        # images = req.FILES.getlist('image')
        # for image in images:
        #     # img = cv2.imread(image.path, cv2.IMREAD_GRAYSCALE)
        #     print(image)
        # for key in req.FILES:
        #     print(req.FILES[key])
        #     file = req.FILES[key]

        #     fs = FileSystemStorage()
        #     if not os.path.exists('file'):
        #         os.makedirs('file')
        #     filename = fs.save('file/'+file.name, file)
        #     file_url = fs.url(filename)
        #     file_url = '.'+file_url
        image = req.FILES['image']
        fs = FileSystemStorage()
        if not os.path.exists('file'):
            os.makedirs('file')
        filename = fs.save('file/'+image.name, image)
        file_url = fs.url(filename)
        file_url = '.'+file_url
        
        # model = YOLO("yolov8n.yaml")  # build a new model from scratch
        # model.train(data="coco128.yaml", epochs=3)
        results = model.predict(file_url)
        res_plotted = results[0].plot()
        # image_b64 = base64.b64encode(res_plotted).decode()
        # print(image_b64)
        # print(res_plotted)

        # 이미지 창에 출력
        # cv2.imshow('Image', res_plotted)
        # cv2.waitKey(0)
        image_data = np.array(res_plotted, dtype=np.uint8)
        # image = cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)  # 이미지 생성 (BGR 형식으로)
        print(image_data)
        # retval, buffer = cv2.imencode('.png', image_data)
        # image_base64 = base64.b64encode(buffer).decode('utf-8')

        # result  = ProductAnalysis()
        # result.image = image_data
        # image = Image.fromarray(image_data.astype('uint8'))
        # print(image)
        # PIL 이미지를 BytesIO를 사용하여 파일로 변환
        # image_io = BytesIO()
        # image.save(image_io, format='PNG')  # 이미지를 PNG 형식으로 저장하거나 원하는 형식으로 변경 가능
        img = cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)
        img = Image.fromarray(img.astype('uint8'))
        
        img.show()
        
        # # 이미지를 BytesIO로 저장
        image_io = BytesIO()
        img.save(image_io, format='PNG')  # 이미지를 원하는 형식으로 저장(PNG, JPEG 등)
        if not os.path.exists('product/detect'):
            os.makedirs('product/detect')
        # BytesIO를 Django의 File 객체로 변환하여 ImageField에 저장
        product_analysis = ProductAnalysis()
        product_analysis.image.save('image.png', File(image_io), save=True)
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