from django.urls import path
from . import views

from query import views

urlpatterns = [
    path('', views.list_queryboards),
    path('detail/<int:query_id>', views.detail_queryboard),
    path('create', views.create_queryboard),
    path('update/<int:query_id>', views.update_queryboard),
    path('delete/<int:query_id>', views.delete_queryboard),
    path('increase_view/<int:query_id>', views.increase_view_queryboard),
    path('like/<int:query_id>', views.like_queryboard),
    path('dislike/<int:query_id>', views.dislike_queryboard),
    path('comment/create/<int:query_id>', views.create_comment),
    path('comment/update/<int:comment_id>', views.update_comment),
    path('comment/delete/<int:comment_id>', views.delete_comment),
    path('comment/like/<int:comment_id>', views.like_comment),
    path('comment/dislike/<int:comment_id>', views.dislike_comment),
]