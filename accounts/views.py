"""
사용자 인증 관련 뷰
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomLoginForm, UserProfileForm
from .models import User


class CustomLoginView(LoginView):
    """커스텀 로그인 뷰"""

    form_class = CustomLoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(
            self.request, f"{form.get_user().get_full_name()}님, 환영합니다!"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "로그인에 실패했습니다. 사용자명과 비밀번호를 확인해주세요."
        )
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """커스텀 로그아웃 뷰"""

    next_page = "accounts:login"

    def get(self, request, *args, **kwargs):
        """GET 요청으로 로그아웃 처리 (Django 5.0+ 호환)"""
        if request.user.is_authenticated:
            messages.info(request, "로그아웃되었습니다.")
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """POST 요청으로 로그아웃 처리"""
        return super().post(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    """프로필 수정 뷰"""

    model = User
    form_class = UserProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "프로필이 수정되었습니다.")
        return super().form_valid(form)


# SSO 로그인 뷰 (향후 구현)
def sso_login(request):
    """
    SSO 로그인 처리
    실제 SSO 연동 시 OAuth2/SAML 처리 로직 구현 필요
    """
    # TODO: SSO 연동 구현
    # 1. SSO 서버로 리다이렉트
    # 2. 콜백 처리
    # 3. 사용자 정보 조회/생성
    # 4. 로그인 처리
    messages.info(request, "SSO 로그인은 현재 개발 중입니다.")
    return redirect("accounts:login")


def sso_callback(request):
    """SSO 콜백 처리"""
    # TODO: SSO 콜백 구현
    return redirect("dashboard:index")
