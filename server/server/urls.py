from django.contrib import admin
from django.urls import path, include

from server import views

urlpatterns = [
    path("api/favorite/", include("favorite.urls")),
    path("api/product/", include("product.urls")),
    path("api/report/", include("report.urls")),
    path("api/alert/", include("alert.urls")),
    path("api/auth/", include("user_auth.urls")),
    path("admin/", admin.site.urls),
    path("test", views.index),
]
