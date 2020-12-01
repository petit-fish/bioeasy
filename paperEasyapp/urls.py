from django.shortcuts import redirect
from django.urls import path
from . import views
from .views import PostListView, PostDetailView

urlpatterns = [
    path('', views.home, name="home"),
    path('second', views.second),
    path('third', views.third, name='third'),
    path('post/', PostListView.as_view(), name='post_list'),
    path('detail/<int:pk>', PostDetailView.as_view(), name='post_detail'),
    path('add/', views.add),
    path('memo/', views.add_memo, name='add_memo'),
    path('add/create', views.create, name='create'),

    path('memo/create_memo', views.create_memo, name='create_memo'),
    path('memo/<int:pk>/delete_memo', views.delete_memo, name='delete_memo'),

    path('post/edit/<int:pk>', views.update, name='update_post'),
    path('post/<int:pk>/delete', views.delete, name='delete_post'),
    path('createcomment/<int:pk>', views.createcomment, name='create_comment'),
    path('createcomment/add/<int:pk>', views.createcomment),
    path('createcomment/delete/<int:pk>', views.deletecomment, name='delete_comment'),
    path('createcomment/edit/<int:pk>', views.updatecomment, name='update_comment'),

    path('keywordToGraph/', views.keywordToGraph),
]
