from django.urls import path
from . import views

from product import views

urlpatterns = [
    path('', views.index),
    path('select', views.select),
    path('analysis', views.analysis),
    path('detect/<str:image_url>', views.get_image , name='detect_image'),
    path('select/product', views.selectProduct),
    
    path('test', views.test),
    path('test2', views.test2),
    path('test3', views.yolotest),
    path('stream/', views.stream_video, name='stream_video'),
]
