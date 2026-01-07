"""
알림 서비스
알림 생성 및 발송 로직
"""

from django.utils import timezone
from datetime import timedelta

from .models import Notification, NotificationSetting
from accounts.models import User


def create_change_notification(regulation, version, exclude_user=None):
    """
    제개정 알림 생성
    사규가 제정/개정/폐지되었을 때 관련 사용자에게 알림 발송
    """
    change_type_labels = {
        'CREATE': '제정',
        'REVISE': '개정',
        'ABOLISH': '폐지',
    }
    
    change_label = change_type_labels.get(version.change_type, '변경')
    
    # 알림 제목 및 내용
    title = f"[{change_label}] {regulation.title}"
    message = f"""
사규가 {change_label}되었습니다.

- 사규코드: {regulation.code}
- 사규명: {regulation.title}
- 버전: v{version.version_number}
- 변경사유: {version.change_reason}
- {change_label}일: {version.created_at.strftime('%Y-%m-%d')}
    """.strip()
    
    # 알림 수신 대상 결정
    if regulation.scope == 'ALL':
        # 전 임직원
        users = User.objects.filter(is_active=True)
    else:
        # 해당 부서만
        users = User.objects.filter(
            is_active=True,
            department=regulation.responsible_dept
        )
    
    # 제외 사용자 처리
    if exclude_user:
        users = users.exclude(pk=exclude_user.pk)
    
    # 알림 생성
    notifications = []
    for user in users:
        # 알림 설정 확인
        try:
            setting = user.notification_setting
            if not setting.receive_change_notification:
                continue
        except NotificationSetting.DoesNotExist:
            pass
        
        notifications.append(Notification(
            user=user,
            regulation=regulation,
            notification_type='CHANGE',
            title=title,
            message=message,
        ))
    
    if notifications:
        Notification.objects.bulk_create(notifications)
    
    return len(notifications)


def create_expiry_notification(regulation, days_until_expiry):
    """
    만료예정 알림 생성
    정기검토일이 다가오는 사규에 대해 책임부서 담당자에게 알림
    """
    title = f"[정기검토예정] {regulation.title}"
    message = f"""
정기검토 예정일이 {days_until_expiry}일 남았습니다.

- 사규코드: {regulation.code}
- 사규명: {regulation.title}
- 정기검토예정일: {regulation.expiry_date.strftime('%Y-%m-%d')}

해당 사규의 유효성을 검토하고, 필요시 개정을 진행해 주세요.
    """.strip()
    
    # 책임부서 담당자에게 알림
    users = User.objects.filter(
        is_active=True,
        department=regulation.responsible_dept,
        role__in=['DEPT_MANAGER', 'COMPLIANCE', 'ADMIN']
    )
    
    notifications = []
    for user in users:
        try:
            setting = user.notification_setting
            if not setting.receive_expiry_notification:
                continue
        except NotificationSetting.DoesNotExist:
            pass
        
        notifications.append(Notification(
            user=user,
            regulation=regulation,
            notification_type='EXPIRY',
            title=title,
            message=message,
        ))
    
    if notifications:
        Notification.objects.bulk_create(notifications)
    
    return len(notifications)


def check_expiry_notifications():
    """
    만료예정 알림 일괄 체크
    정기적으로 실행하여 만료예정 사규를 확인하고 알림 생성
    """
    from regulations.models import Regulation
    
    today = timezone.now().date()
    alert_days = [30, 7]  # 30일, 7일 전 알림
    
    total_notifications = 0
    
    for days in alert_days:
        target_date = today + timedelta(days=days)
        
        regulations = Regulation.objects.filter(
            status='ACTIVE',
            expiry_date=target_date
        )
        
        for regulation in regulations:
            count = create_expiry_notification(regulation, days)
            total_notifications += count
    
    return total_notifications


def create_review_notification(regulation, requester):
    """
    검토요청 알림 생성
    책임부서에서 제개정을 요청할 때 관리부서(준법지원인)에게 알림
    """
    title = f"[검토요청] {regulation.title}"
    message = f"""
사규 검토 요청이 접수되었습니다.

- 사규코드: {regulation.code}
- 사규명: {regulation.title}
- 요청자: {requester.get_full_name()} ({requester.department.name if requester.department else '-'})
- 요청일: {timezone.now().strftime('%Y-%m-%d %H:%M')}

검토 후 승인 또는 반려 처리를 진행해 주세요.
    """.strip()
    
    # 준법지원인 및 관리자에게 알림
    users = User.objects.filter(
        is_active=True,
        role__in=['COMPLIANCE', 'ADMIN']
    )
    
    notifications = []
    for user in users:
        try:
            setting = user.notification_setting
            if not setting.receive_review_notification:
                continue
        except NotificationSetting.DoesNotExist:
            pass
        
        notifications.append(Notification(
            user=user,
            regulation=regulation,
            notification_type='REVIEW',
            title=title,
            message=message,
        ))
    
    if notifications:
        Notification.objects.bulk_create(notifications)
    
    return len(notifications)






