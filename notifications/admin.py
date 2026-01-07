"""
알림 관리자 페이지 설정
- Django Admin에서는 알림 관리를 제외합니다.
- 알림 발송은 웹 인터페이스(/notifications/create/)를 통해 관리합니다.
"""

from django.contrib import admin
from .models import Notification, NotificationSetting

# 알림 관리는 Django Admin에서 제외
# 웹 인터페이스에서 관리합니다.






