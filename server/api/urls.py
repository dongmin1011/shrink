from django.urls import path
from . import views

from api import views

urlpatterns = [
    path("", views.index),
    path("auth/code", views.send_auth_code),
    path("auth/code/check", views.check_auth_code),
    path("redis-test", views.set_value),
    path("redis-test/<str:key>", views.get_value),

    # path("user/<str:phone>/auth", views.send_auth_code),
    # path("user/<str:phone>/auth", views.get_auth_code),
]
