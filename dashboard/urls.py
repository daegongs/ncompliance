"""
대시보드 URL 설정
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/regulation/<int:pk>/', views.regulation_content, name='regulation_content'),
    path('api/favorite/<int:pk>/toggle/', views.toggle_favorite, name='toggle_favorite'),
]


