"""
알림 URL 설정
"""

from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('create/', views.notification_create, name='create'),
    path('<int:pk>/', views.notification_detail, name='detail'),
    path('<int:pk>/read/', views.mark_as_read, name='mark_read'),
    path('<int:pk>/update/', views.notification_update, name='update'),
    path('<int:pk>/delete/', views.notification_delete, name='delete'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    path('settings/', views.notification_settings, name='settings'),
    path('unread-count/', views.unread_count, name='unread_count'),
]








