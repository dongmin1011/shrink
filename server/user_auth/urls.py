from django.urls import path
from . import views

from user_auth import views

urlpatterns = [
    path("code", views.send_auth_code),
    path("code/check", views.check_auth_code),
    path("register", views.register),
    path("login", views.login),
    path('user/profile-image', views.upload_profile_image),
    path('user/password', views.update_password),
    path('user/nickname', views.update_nickname),
]
