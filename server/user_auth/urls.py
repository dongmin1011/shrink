from django.urls import path
from . import views

from user_auth import views

urlpatterns = [
    path("code", views.send_auth_code),
    path("code/check", views.check_auth_code),
    path("register", views.register_user),
    path("login", views.login_user),
    path('user/info', views.get_user_info),
    path('user/profile-image', views.update_profile_image),
    path('user/password', views.update_password),
    path('user/nickname', views.update_nickname),
    path('user/delete', views.delete_user),
]
