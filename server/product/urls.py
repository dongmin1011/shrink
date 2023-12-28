from django.urls import path
from . import views

from product import views

urlpatterns = [
    path('', views.index),
    path('select', views.select),
    path('analysis', views.analysis),
    path('detect/<str:image_url>', views.get_image , name='detect_image'),
]
