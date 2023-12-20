from django.urls import path
from . import views

from favorite import views

urlpatterns = [
    path('', views.index),
]
