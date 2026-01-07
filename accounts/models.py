"""
사용자 및 부서 모델
User and Department models for nCompliance
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Company(models.Model):
    """
    법인 모델
    그룹사 또는 계열사를 관리하는 모델
    """
    name = models.CharField('법인명', max_length=100)
    code = models.CharField('법인코드', max_length=20, unique=True)
    is_active = models.BooleanField('활성화', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        verbose_name = '법인'
        verbose_name_plural = '법인'
        ordering = ['code']

    def __str__(self):
        return self.name


class Department(models.Model):
    """
    부서 모델
    회사의 조직 구조를 표현하는 계층적 부서 모델
    """
    name = models.CharField('부서명', max_length=100)
    code = models.CharField('부서코드', max_length=20, unique=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departments',
        verbose_name='소속법인'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='상위부서'
    )
    is_active = models.BooleanField('활성화', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        verbose_name = '부서'
        verbose_name_plural = '부서'
        ordering = ['code']

    def __str__(self):
        return self.name

    def get_full_path(self):
        """상위 부서를 포함한 전체 경로 반환"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class User(AbstractUser):
    """
    사용자 모델 (Django AbstractUser 확장)
    SSO 연동 및 역할 기반 권한 관리 지원
    """
    ROLE_CHOICES = [
        ('GENERAL', '일반'),
        ('DEPT_MANAGER', '책임부서담당'),
        ('COMPLIANCE', '준법지원인'),
        ('ADMIN', '관리자'),
    ]

    employee_id = models.CharField('사번', max_length=20, unique=True, null=True, blank=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name='소속법인'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        verbose_name='소속부서'
    )
    role = models.CharField('역할', max_length=20, choices=ROLE_CHOICES, default='GENERAL')
    phone = models.CharField('연락처', max_length=20, blank=True)
    position = models.CharField('직위', max_length=50, blank=True)
    
    # SSO 관련 필드
    sso_id = models.CharField('SSO ID', max_length=100, unique=True, null=True, blank=True)
    last_sso_login = models.DateTimeField('마지막 SSO 로그인', null=True, blank=True)

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자'

    def __str__(self):
        if self.department:
            return f"{self.get_full_name()} ({self.department.name})"
        return self.get_full_name() or self.username

    def get_full_name(self):
        """성명 반환 (first_name + last_name 또는 username)"""
        full_name = f"{self.last_name}{self.first_name}".strip()
        return full_name if full_name else self.username

    def is_compliance_officer(self):
        """준법지원인 여부"""
        return self.role == 'COMPLIANCE'

    def is_dept_manager(self):
        """책임부서 담당자 여부"""
        return self.role == 'DEPT_MANAGER'

    def can_manage_regulations(self):
        """사규 관리 권한 여부"""
        return self.role in ['DEPT_MANAGER', 'COMPLIANCE', 'ADMIN']





