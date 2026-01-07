"""
사용자 인증 관련 폼
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class CustomLoginForm(AuthenticationForm):
    """커스텀 로그인 폼"""
    username = forms.CharField(
        label='사용자명',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '사용자명 또는 사번 입력',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호 입력'
        })
    )


class UserProfileForm(forms.ModelForm):
    """사용자 프로필 수정 폼"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'position']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': '이름',
            'last_name': '성',
            'email': '이메일',
            'phone': '연락처',
            'position': '직위',
        }






