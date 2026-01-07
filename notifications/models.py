"""
알림 모델
Notification models for nCompliance
"""

from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    알림 모델
    사규 제개정, 만료예정 등의 알림 관리
    """
    TYPE_CHOICES = [
        ('CHANGE', '제개정알림'),
        ('EXPIRY', '만료예정알림'),
        ('REVIEW', '검토요청알림'),
        ('SYSTEM', '시스템알림'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='수신자'
    )
    regulation = models.ForeignKey(
        'regulations.Regulation',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='관련사규'
    )
    notification_type = models.CharField('알림유형', max_length=20, choices=TYPE_CHOICES)
    title = models.CharField('제목', max_length=200)
    message = models.TextField('내용')
    is_read = models.BooleanField('읽음여부', default=False)
    read_at = models.DateTimeField('읽은시간', null=True, blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)

    class Meta:
        verbose_name = '알림'
        verbose_name_plural = '알림'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title}"

    def get_type_icon(self):
        """알림 유형별 아이콘"""
        icons = {
            'CHANGE': 'bi-pencil-square',
            'EXPIRY': 'bi-clock-history',
            'REVIEW': 'bi-clipboard-check',
            'SYSTEM': 'bi-info-circle',
        }
        return icons.get(self.notification_type, 'bi-bell')

    def get_type_color(self):
        """알림 유형별 색상"""
        colors = {
            'CHANGE': 'primary',
            'EXPIRY': 'warning',
            'REVIEW': 'info',
            'SYSTEM': 'secondary',
        }
        return colors.get(self.notification_type, 'secondary')


class NotificationSetting(models.Model):
    """
    알림 설정 모델
    사용자별 알림 수신 설정
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_setting',
        verbose_name='사용자'
    )
    receive_change_notification = models.BooleanField('제개정알림수신', default=True)
    receive_expiry_notification = models.BooleanField('만료예정알림수신', default=True)
    receive_review_notification = models.BooleanField('검토요청알림수신', default=True)
    email_notification = models.BooleanField('이메일알림', default=False)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        verbose_name = '알림 설정'
        verbose_name_plural = '알림 설정'

    def __str__(self):
        return f"{self.user.username}의 알림 설정"





