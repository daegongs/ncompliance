"""
사용자/부서/법인 관리자 페이지 설정
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from .models import User, Department, Company

# Django 기본 Group은 사용하지 않으므로 admin에서 제거
admin.site.unregister(Group)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """법인 관리"""
    list_display = ['code', 'name', 'department_count', 'user_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['code']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    def department_count(self, obj):
        """소속 부서 수"""
        return obj.departments.count()
    department_count.short_description = '부서 수'
    
    def user_count(self, obj):
        """소속 사용자 수"""
        return User.objects.filter(company=obj).count()
    user_count.short_description = '사용자 수'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """부서 관리"""
    list_display = ['code', 'name', 'company', 'parent', 'user_count', 'regulation_count', 'is_active']
    list_filter = ['is_active', 'company']
    search_fields = ['code', 'name']
    ordering = ['company', 'code']
    list_editable = ['is_active']
    raw_id_fields = ['parent']  # 자기 참조는 raw_id_fields 사용
    readonly_fields = ['created_at', 'updated_at']
    
    def user_count(self, obj):
        """소속 사용자 수"""
        return obj.members.count()
    user_count.short_description = '사용자'
    
    def regulation_count(self, obj):
        """책임 사규 수"""
        return obj.regulations.count()
    regulation_count.short_description = '사규'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """사용자 관리"""
    list_display = [
        'username', 'employee_id', 'get_full_name', 'email',
        'company', 'department', 'role_badge', 'is_active', 'last_login'
    ]
    list_filter = ['role', 'company', 'department', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'employee_id', 'first_name', 'last_name', 'email', 'phone']
    ordering = ['username']
    autocomplete_fields = ['company', 'department']
    list_per_page = 50
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('소속 정보', {
            'fields': ('employee_id', 'company', 'department', 'role', 'phone', 'position')
        }),
        ('SSO 정보', {
            'fields': ('sso_id', 'last_sso_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('소속 정보', {
            'fields': ('employee_id', 'company', 'department', 'role', 'phone', 'position')
        }),
    )
    
    def role_badge(self, obj):
        """역할 배지 표시"""
        colors = {
            'ADMIN': '#dc3545',      # 빨강
            'COMPLIANCE': '#0d6efd', # 파랑
            'DEPT_MANAGER': '#198754', # 초록
            'GENERAL': '#6c757d',    # 회색
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = '역할'
    role_badge.admin_order_field = 'role'
    
    actions = ['activate_users', 'deactivate_users']
    
    @admin.action(description='선택한 사용자 활성화')
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    
    @admin.action(description='선택한 사용자 비활성화')
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)



