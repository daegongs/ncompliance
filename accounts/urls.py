"""
사용자 인증 URL 설정
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    # SSO 관련 URL
    path('sso/login/', views.sso_login, name='sso_login'),
    path('sso/callback/', views.sso_callback, name='sso_callback'),
]


