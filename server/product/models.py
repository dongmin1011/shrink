import uuid
from django.db import models
from django.utils import timezone

from user_auth.models import User

# class Code(models.Model):
#     code = models.CharField(max_length=5)

#상품정보 저장 DB
class Product(models.Model):
    product_id = models.CharField(max_length=10, primary_key=True)  # custom_id를 기본 키로 설정

    product_name = models.CharField(max_length=100)
    detail = models.CharField(max_length=50,null=True) #mean
    weight = models.CharField(max_length=50,null=True)
    create_at = models.DateTimeField(default=timezone.now)
    # code = models.ForeignKey(Code, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, upload_to='product/image/')

#상품의 가격변화를 저장하는 DB
class PriceChange(models.Model):
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    date = models.DateField()
    price = models.CharField(max_length=50,null=True)
    max_price = models.CharField(max_length=50,null=True)
    min_price = models.CharField(max_length=50,null=True)

    
# Create your models here.
#yolo이미지 분석 결과를 저장하는 DB
class ProductAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    image = models.ImageField(blank=True, upload_to='product/detect/')
    user = models.ForeignKey(User, on_delete=models.CASCADE,  null=True)

    
    is_reading = models.BooleanField(default=False)
    create_at = models.DateTimeField(default=timezone.now)
    
class ProductAnalysisResults(models.Model):
    productAnalysis = models.ForeignKey(ProductAnalysis, on_delete=models.CASCADE)
    
    product = models.ForeignKey(Product , on_delete=models.CASCADE, null=True)
    result = models.CharField(max_length=100,null=True)
    weight = models.CharField(max_length=50,null=True)