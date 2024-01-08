import uuid
from django.db import models
from user_auth.models import User

from django.utils import timezone
from product.models import Product

class Report(models.Model):
    
    STATUS_CHOICES = [
        (1, '보류'),
        (2, '의심'),
        (3, '슈링크'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product =  models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    product_name = models.CharField(max_length=100)
    price = models.IntegerField()
    weight = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)
    content = models.CharField(max_length=500, default="")
    unit = models.CharField(max_length=10, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    
    class Meta:
        db_table = 'report'
        
class ReportImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, upload_to='report/image/')


class Like(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='report_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        unique_together = ('report', 'user')
        db_table = 'report_like'
        
class ShrinkFlationGeneration(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, unique=True)
    before = models.CharField(max_length=10, null=True)
    after = models.CharField(max_length=10, null=True)