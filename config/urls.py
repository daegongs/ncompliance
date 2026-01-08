"""
URL configuration for nCompliance project.
사규관리 시스템 URL 설정
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Django Admin 사이트 커스터마이징
admin.site.site_header = 'nCompliance 관리자'
admin.site.site_title = 'nCompliance Admin'
admin.site.index_title = '사규관리 시스템 관리'

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # 메인 대시보드
    path('', include('dashboard.urls')),
    
    # 사용자 인증
    path('accounts/', include('accounts.urls')),
    
    # 사규 관리
    path('regulations/', include('regulations.urls')),
    
    # 알림
    path('notifications/', include('notifications.urls')),
    
    # 보고서
    path('reports/', include('reports.urls')),
]

# 개발 환경에서 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)










