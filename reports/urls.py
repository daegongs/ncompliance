"""
보고서 URL 설정
"""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_index, name='index'),
    
    # 사규 현황 보고서
    path('status/', views.regulation_status_report, name='status'),
    path('status/export/', views.export_regulation_status_excel, name='status_export'),
    
    # 제개정 이력 보고서
    path('history/', views.change_history_report, name='history'),
    path('history/export/', views.export_change_history_excel, name='history_export'),
    
    # 부서별 보고서
    path('department/', views.department_report, name='department'),
    
    # 만료예정 보고서
    path('expiry/', views.expiry_report, name='expiry'),
    path('expiry/export/', views.export_expiry_excel, name='expiry_export'),
]






