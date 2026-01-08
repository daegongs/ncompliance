"""
사규 관리자 페이지 설정
"""

from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Regulation, RegulationVersion, RegulationTag, RegulationDownloadLog, Favorite, CommonCode


class RegulationVersionInline(admin.TabularInline):
    """사규 버전 인라인"""
    model = RegulationVersion
    extra = 0
    readonly_fields = ['created_at', 'created_by']
    ordering = ['-created_at']


class FavoriteInline(admin.TabularInline):
    """즐겨찾기 인라인"""
    model = Favorite
    extra = 0
    readonly_fields = ['user', 'created_at']
    can_delete = True


@admin.register(Regulation)
class RegulationAdmin(admin.ModelAdmin):
    """사규 관리"""
    list_display = [
        'code', 'title', 'category', 'group', 'status', 'is_public',
        'responsible_dept', 'manager', 'current_version', 'effective_date', 'has_file'
    ]
    list_filter = ['category', 'status', 'is_mandatory', 'is_public', 'access_level', 'group', 'responsible_dept']
    search_fields = ['code', 'title', 'description', 'manager', 'manager_primary', 'group']
    ordering = ['category', 'code']
    date_hierarchy = 'created_at'
    inlines = [RegulationVersionInline, FavoriteInline]
    raw_id_fields = ['responsible_dept', 'parent_regulation', 'created_by']
    filter_horizontal = ['related_regulations', 'allowed_companies', 'allowed_departments', 'allowed_users']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('code', 'title', 'category', 'group', 'description')
        }),
        ('효력 정보', {
            'fields': ('is_mandatory', 'scope', 'status')
        }),
        ('담당 정보', {
            'fields': ('responsible_dept', 'manager', 'manager_primary', 'is_public', 'created_by')
        }),
        ('버전 및 일자', {
            'fields': ('current_version', 'effective_date', 'expiry_date', 'abolished_date')
        }),
        ('사규 본문 및 파일', {
            'fields': ('content', 'original_file', 'reference_url'),
            'description': '사규 본문, 원본 파일, 참조 링크를 관리합니다.'
        }),
        ('연관 사규', {
            'fields': ('parent_regulation', 'related_regulations'),
            'classes': ('collapse',)
        }),
        ('접근 권한', {
            'fields': ('access_level', 'allowed_companies', 'allowed_departments', 'allowed_users'),
            'description': '사규에 접근할 수 있는 대상을 지정합니다.',
            'classes': ('collapse',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_file(self, obj):
        """원본 파일 존재 여부"""
        if obj.original_file:
            return mark_safe('<span style="color: green;">●</span> 있음')
        return mark_safe('<span style="color: gray;">○</span> 없음')
    has_file.short_description = '원본파일'


@admin.register(RegulationVersion)
class RegulationVersionAdmin(admin.ModelAdmin):
    """사규 버전 관리"""
    list_display = [
        'regulation', 'version_number', 'change_type', 
        'approved_by', 'approved_at', 'created_by', 'created_at'
    ]
    list_filter = ['change_type', 'approved_at']
    search_fields = ['regulation__code', 'regulation__title', 'change_reason']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['regulation', 'approved_by', 'created_by']


@admin.register(RegulationTag)
class RegulationTagAdmin(admin.ModelAdmin):
    """태그 관리"""
    list_display = ['name', 'get_regulation_count', 'created_at']
    search_fields = ['name']
    filter_horizontal = ['regulations']

    def get_regulation_count(self, obj):
        return obj.regulations.count()
    get_regulation_count.short_description = '사규 수'


@admin.register(RegulationDownloadLog)
class RegulationDownloadLogAdmin(admin.ModelAdmin):
    """다운로드 로그"""
    list_display = ['regulation', 'version', 'user', 'ip_address', 'downloaded_at']
    list_filter = ['downloaded_at']
    search_fields = ['regulation__code', 'user__username']
    ordering = ['-downloaded_at']
    date_hierarchy = 'downloaded_at'
    readonly_fields = ['regulation', 'version', 'user', 'ip_address', 'downloaded_at']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """즐겨찾기 관리"""
    list_display = ['user', 'regulation', 'created_at']
    list_filter = ['created_at', 'regulation__category', 'regulation__group']
    search_fields = ['user__username', 'user__first_name', 'regulation__title', 'regulation__code']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user', 'regulation']
    readonly_fields = ['created_at']


@admin.register(CommonCode)
class CommonCodeAdmin(admin.ModelAdmin):
    """공통코드 관리"""
    list_display = ['code_type', 'code', 'name', 'sort_order', 'is_active', 'is_system', 'updated_at']
    list_filter = ['code_type', 'is_active', 'is_system']
    search_fields = ['code', 'name', 'description']
    ordering = ['code_type', 'sort_order', 'code']
    list_editable = ['sort_order', 'is_active']
    list_per_page = 50
    raw_id_fields = ['parent']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('code_type', 'code', 'name', 'description')
        }),
        ('설정', {
            'fields': ('sort_order', 'is_active', 'is_system', 'parent')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_codes', 'deactivate_codes']
    
    @admin.action(description='선택한 코드 활성화')
    def activate_codes(self, request, queryset):
        queryset.update(is_active=True)
    
    @admin.action(description='선택한 코드 비활성화')
    def deactivate_codes(self, request, queryset):
        queryset.filter(is_system=False).update(is_active=False)
    
    def delete_model(self, request, obj):
        """시스템 코드는 삭제 불가"""
        if obj.is_system:
            from django.contrib import messages
            messages.error(request, f"시스템 코드 '{obj.name}'은(는) 삭제할 수 없습니다.")
            return
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """시스템 코드는 삭제 불가"""
        system_codes = queryset.filter(is_system=True)
        if system_codes.exists():
            from django.contrib import messages
            messages.warning(request, "시스템 코드는 삭제되지 않았습니다.")
        queryset.filter(is_system=False).delete()



    list_per_page = 50
    raw_id_fields = ['parent']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('code_type', 'code', 'name', 'description')
        }),
        ('설정', {
            'fields': ('sort_order', 'is_active', 'is_system', 'parent')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_codes', 'deactivate_codes']
    
    @admin.action(description='선택한 코드 활성화')
    def activate_codes(self, request, queryset):
        queryset.update(is_active=True)
    
    @admin.action(description='선택한 코드 비활성화')
    def deactivate_codes(self, request, queryset):
        queryset.filter(is_system=False).update(is_active=False)
    
    def delete_model(self, request, obj):
        """시스템 코드는 삭제 불가"""
        if obj.is_system:
            from django.contrib import messages
            messages.error(request, f"시스템 코드 '{obj.name}'은(는) 삭제할 수 없습니다.")
            return
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """시스템 코드는 삭제 불가"""
        system_codes = queryset.filter(is_system=True)
        if system_codes.exists():
            from django.contrib import messages
            messages.warning(request, "시스템 코드는 삭제되지 않았습니다.")
        queryset.filter(is_system=False).delete()


