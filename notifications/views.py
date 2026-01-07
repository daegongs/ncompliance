"""
알림 뷰
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Notification, NotificationSetting
from accounts.models import User


def is_admin(user):
    """시스템 관리자 여부 확인"""
    return user.is_superuser or (hasattr(user, 'role') and user.role == 'ADMIN')


@login_required
def notification_list(request):
    """알림 목록"""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # 페이지네이션
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 안 읽은 알림 수
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'notifications/notification_list.html', {
        'page_obj': page_obj,
        'unread_count': unread_count,
    })


@login_required
def notification_detail(request, pk):
    """알림 상세 및 읽음 처리"""
    notification = get_object_or_404(
        Notification, 
        pk=pk, 
        user=request.user
    )
    
    # 읽음 처리
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
    
    # 관련 사규가 있으면 사규 상세로 리다이렉트
    if notification.regulation:
        return redirect('regulations:detail', pk=notification.regulation.pk)
    
    return render(request, 'notifications/notification_detail.html', {
        'notification': notification,
    })


@login_required
def mark_as_read(request, pk):
    """알림 읽음 처리 (AJAX)"""
    if request.method == 'POST':
        notification = get_object_or_404(
            Notification,
            pk=pk,
            user=request.user
        )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)


@login_required
def mark_all_as_read(request):
    """모든 알림 읽음 처리"""
    if request.method == 'POST':
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect('notifications:list')
    
    return redirect('notifications:list')


@login_required
def notification_settings(request):
    """알림 설정"""
    setting, created = NotificationSetting.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        setting.receive_change_notification = request.POST.get('receive_change', '') == 'on'
        setting.receive_expiry_notification = request.POST.get('receive_expiry', '') == 'on'
        setting.receive_review_notification = request.POST.get('receive_review', '') == 'on'
        setting.email_notification = request.POST.get('email_notification', '') == 'on'
        setting.save()
        
        return redirect('notifications:settings')
    
    return render(request, 'notifications/settings.html', {
        'setting': setting,
    })


@login_required
def unread_count(request):
    """안 읽은 알림 수 반환 (AJAX)"""
    count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'count': count})


@login_required
@user_passes_test(is_admin)
def notification_create(request):
    """알림 등록 (관리자 전용)"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        notification_type = request.POST.get('notification_type', 'SYSTEM')
        target = request.POST.get('target', 'all')  # all, role, user
        target_role = request.POST.get('target_role', '')
        target_users = request.POST.getlist('target_users', [])
        
        if not title or not message:
            messages.error(request, '제목과 내용은 필수 입력 항목입니다.')
            return redirect('notifications:create')
        
        # 대상 사용자 결정
        if target == 'all':
            users = User.objects.filter(is_active=True)
        elif target == 'role' and target_role:
            users = User.objects.filter(is_active=True, role=target_role)
        elif target == 'user' and target_users:
            users = User.objects.filter(pk__in=target_users, is_active=True)
        else:
            users = User.objects.filter(is_active=True)
        
        # 알림 생성
        created_count = 0
        for user in users:
            Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
            )
            created_count += 1
        
        messages.success(request, f'{created_count}명에게 알림이 발송되었습니다.')
        return redirect('notifications:list')
    
    # GET 요청
    users = User.objects.filter(is_active=True).order_by('username')
    role_choices = User.ROLE_CHOICES if hasattr(User, 'ROLE_CHOICES') else []
    type_choices = Notification.TYPE_CHOICES
    
    return render(request, 'notifications/notification_create.html', {
        'users': users,
        'role_choices': role_choices,
        'type_choices': type_choices,
    })


@login_required
@user_passes_test(is_admin)
def notification_delete(request, pk):
    """알림 삭제 (관리자 전용)"""
    notification = get_object_or_404(Notification, pk=pk)
    
    if request.method == 'POST':
        notification.delete()
        messages.success(request, '알림이 삭제되었습니다.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect('notifications:list')
    
    return redirect('notifications:list')






