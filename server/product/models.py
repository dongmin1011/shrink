import uuid
from django.db import models
from django.utils import timezone

from user_auth.models import User

# Create your models here.
class ProductAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    image = models.ImageField(blank=True, upload_to='product/detect/')
    user = models.ForeignKey(User, on_delete=models.CASCADE,  null=True)

    # answer = models.CharField(max_length=10,null=True)
    # result = models.CharField(max_length=10)
    # is_correct= models.BooleanField(default=False)
    # pub_date = models.DateTimeField('date published')
    result = models.CharField(max_length=100,null=True)
    weight = models.CharField(max_length=50,null=True)
    create_at = models.DateTimeField(default=timezone.now)