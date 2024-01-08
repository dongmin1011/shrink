from django.urls import path
from . import views

from product import views

urlpatterns = [
    path('', views.index),
    # path('select', views.select),
    path('selectall', views.selectall),
    path('select/detail/<str:query_id>', views.select_id),
    path('get_image/<str:url>', views.get_image ),
    
    path('analysis', views.analysis),
    path('detect/<str:image_url>', views.get_analysis_image , name='detect_image'),
    path('select/priceChange', views.selectProduct),
    path('select/analysis_list', views.token_analysis_list),
    path('delete/analysis_list', views.delete_analysis_list),
    path('update/analysis', views.read_update),
    
    path('search', views.search_product),
    
    path('upload_image/<str:query_id>', views.upload_product_image),
    path('upload_new_product', views.upload_new_product),

    
    # path('test', views.test),
    # path('test2', views.test2),
    path('test3', views.yolotest),
    path('stream/', views.stream_video, name='stream_video'),
]
