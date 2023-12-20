from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import uuid
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)
    nickname = models.CharField(max_length=50)
    profile_url = models.URLField(max_length=200, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.nickname
