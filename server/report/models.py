import uuid
from django.db import models
from user_auth.models import User

from django.utils import timezone

class Report(models.Model):
    
    STATUS_CHOICES = [
        (1, '접수'),
        (2, '처리중'),
        (3, '완료'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    price = models.IntegerField()
    weight = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)
    content = models.CharField(max_length=500, default="")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    
    class Meta:
        db_table = 'report'
        
class ReportImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, upload_to='report/image/')
