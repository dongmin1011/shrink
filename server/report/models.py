from django.db import models
from user_auth.models import User

from django.utils import timezone

# Create your models here.
class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    weight = models.CharField(max_length=50)
    price = models.IntegerField()
    product_name = models.CharField(max_length=100)
