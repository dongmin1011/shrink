from django.urls import path
from . import views

from api import views

urlpatterns = [
    path("", views.index),
    path("auth/code", views.send_auth_code),
    path("auth/code/check", views.check_auth_code),
    path("auth/register", views.register),
    path("auth/login", views.login),

    path('report', views.write_report),

    # path("redis-test", views.set_value),
    # path("redis-test/<str:key>", views.get_value),
]
