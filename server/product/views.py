from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv
load_dotenv()

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
