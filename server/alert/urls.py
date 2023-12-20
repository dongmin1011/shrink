from django.urls import path
from . import views

from alert import views

urlpatterns = [
    path('', views.index),
]
