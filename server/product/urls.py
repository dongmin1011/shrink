from django.urls import path
from . import views

from product import views

urlpatterns = [
    path('', views.index),
    path('select/', views.select),
]
