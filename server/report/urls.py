from django.urls import path
from . import views

from report import views

urlpatterns = [
    path('', views.write_report),
]
