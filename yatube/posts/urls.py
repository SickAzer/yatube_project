from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('group/<slug:slug>/', views.GroupListView.as_view(), name='group_list'),
    path('profile/<str:username>/', views.ProfileListView.as_view(), name='profile'),
    path('posts/<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path('posts/<int:post_id>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('posts/<int:post_id>/comment', views.CommentCreateView.as_view(), name='add_comment'),
    path(
        'posts/<int:post_id>/comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(), name='delete_comment'
    ),
    path('follow/', views.FollowIndexListView.as_view(), name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.FollowCreateView.as_view(),
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.FollowDeleteView.as_view(),
        name='profile_unfollow'
    ),
    path('group_create/', views.GroupCreateView.as_view(), name='group_create'),
    path('group/<slug:slug>/delete/', views.GroupDeleteView.as_view(), name='group_delete'),
    path('liked/', views.like_unlike_post, name='like_unlike_post'),
]
