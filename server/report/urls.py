from django.urls import path
from . import views

from report import views

urlpatterns = [
    path('create', views.write_report),
    path('selectall', views.selectALL),
    path('select', views.select),
    path('selectuser', views.selectUser),
    path('delete/<int:query_id>', views.delete_report),
    path('select/detail/<int:query_id>', views.select_detail),
    path('update/<int:query_id>', views.update_report),
    path('like/<int:query_id>', views.like_report),
     path('likeall', views.user_like_all),
    
    
    path('is_like/<int:query_id>', views.is_like),          #로그인 유저가 좋아요를 눌렀는지 확인
    path('is_report/<int:query_id>', views.is_your_report), #로그인 유저의 게시물인지 확인
    
    
    
    path('select/image/<str:image_url>', views.get_image),
]
