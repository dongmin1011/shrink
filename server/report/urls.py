from django.urls import path
from . import views

from report import views

urlpatterns = [
    path('create', views.write_report),
    path('selectall', views.selectALL),
    path('select', views.select),
    path('selectuser', views.selectUser),
    path('delete/<int:query_id>', views.delete_report),
    
    path('select/image/<str:image_url>', views.get_image),
]
