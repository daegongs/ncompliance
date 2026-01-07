"""
사규 관리 폼
"""

from django import forms
from django.conf import settings
from .models import Regulation, RegulationVersion, RegulationTag
from accounts.models import Company, Department, User


class RegulationForm(forms.ModelForm):
    """사규 등록/수정 폼"""
    
    # 그룹 선택 필드 (필수)
    GROUP_CHOICES = [
        ('', '-- 그룹 선택 --'),
        ('이사회', '이사회'),
        ('HR', 'HR'),
        ('재무', '재무'),
        ('구매', '구매'),
        ('준법', '준법'),
        ('반부패', '반부패'),
        ('정보보호', '정보보호'),
        ('개인정보보호', '개인정보보호'),
        ('안전보건', '안전보건'),
        ('ESG', 'ESG'),
        ('컴플라이언스', '컴플라이언스'),
        ('기타', '기타'),
    ]
    
    group = forms.ChoiceField(
        label='그룹',
        choices=GROUP_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='사규가 속하는 그룹을 선택하세요.'
    )
    
    tags = forms.CharField(
        label='태그',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '콤마(,)로 구분하여 입력'
        }),
        help_text='예: 인사, 재무, 보안'
    )

    class Meta:
        model = Regulation
        fields = [
            'title', 'category', 'group', 'description',
            'is_mandatory', 'scope', 'responsible_dept', 'manager',
            'manager_primary',
            'effective_date', 'expiry_date',
            'parent_regulation', 'related_regulations',
            'access_level', 'is_public', 'allowed_companies', 'allowed_departments', 'allowed_users',
            'original_file', 'content', 'reference_url'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '사규명 입력'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'group': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '사규에 대한 간략한 설명'
            }),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'scope': forms.Select(attrs={'class': 'form-select'}),
            'responsible_dept': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '사규관리 담당자 이름'
            }),
            'manager_primary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '사규관리 책임자 이름'
            }),
            'effective_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'parent_regulation': forms.Select(attrs={'class': 'form-select'}),
            'related_regulations': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5
            }),
            'access_level': forms.Select(attrs={'class': 'form-select'}),
            'allowed_companies': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5
            }),
            'allowed_departments': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5
            }),
            'allowed_users': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5
            }),
            'original_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx,.doc,.hwp,.hwpx'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '규정 본문 내용을 입력하세요'
            }),
            'reference_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/regulation'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 필수 필드 설정
        self.fields['title'].required = True
        self.fields['category'].required = True
        self.fields['responsible_dept'].required = True
        self.fields['access_level'].required = True
        
        # 선택적 필드 설정
        self.fields['description'].required = False
        self.fields['effective_date'].required = False
        self.fields['expiry_date'].required = False
        self.fields['parent_regulation'].required = False
        self.fields['related_regulations'].required = False
        self.fields['original_file'].required = False
        self.fields['content'].required = False
        self.fields['reference_url'].required = False
        self.fields['manager'].required = False
        self.fields['manager_primary'].required = False
        
        self.fields['parent_regulation'].queryset = Regulation.objects.exclude(
            pk=self.instance.pk if self.instance.pk else None
        )
        self.fields['related_regulations'].queryset = Regulation.objects.exclude(
            pk=self.instance.pk if self.instance.pk else None
        )
        
        # 기존 태그 로드
        if self.instance.pk:
            tags = self.instance.tags.values_list('name', flat=True)
            self.initial['tags'] = ', '.join(tags)
            # 기존 그룹 값 로드
            if self.instance.group:
                self.initial['group'] = self.instance.group
        
        # 수정 모드일 때는 코드 필드를 읽기 전용으로 표시
        if self.instance.pk:
            self.fields['code'] = forms.CharField(
                label='사규코드',
                required=False,
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'readonly': True,
                    'disabled': True
                }),
                help_text='사규코드는 수정할 수 없습니다.'
            )
            self.fields['code'].initial = self.instance.code

    def save(self, commit=True):
        # 코드가 없으면 자동 생성 (등록 모드)
        if not self.instance.pk and not self.instance.code:
            self.instance.code = Regulation.generate_code(self.instance.category)
        
        instance = super().save(commit=commit)
        
        if commit:
            # 태그 처리
            tag_names = [t.strip() for t in self.cleaned_data.get('tags', '').split(',') if t.strip()]
            
            # 기존 태그 제거
            instance.tags.clear()
            
            # 새 태그 추가
            for name in tag_names:
                tag, _ = RegulationTag.objects.get_or_create(name=name)
                tag.regulations.add(instance)
        
        return instance


class RegulationVersionForm(forms.ModelForm):
    """사규 버전 등록 폼"""
    
    class Meta:
        model = RegulationVersion
        fields = ['version_number', 'change_type', 'change_reason', 'change_summary', 'content_file']
        widgets = {
            'version_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '예: 1.0, 1.1, 2.0'
            }),
            'change_type': forms.Select(attrs={'class': 'form-select'}),
            'change_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '변경 사유를 입력하세요'
            }),
            'change_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '주요 변경 내용을 요약하여 입력하세요'
            }),
            'content_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx,.doc,.hwp,.hwpx'
            }),
        }

    def clean_content_file(self):
        """첨부파일 유효성 검사"""
        file = self.cleaned_data.get('content_file')
        if file:
            ext = file.name.split('.')[-1].lower()
            allowed_extensions = ['pdf', 'docx', 'doc', 'hwp', 'hwpx']
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'허용되지 않는 파일 형식입니다. ({", ".join(allowed_extensions)})'
                )
            # 파일 크기 제한 (10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('파일 크기는 10MB를 초과할 수 없습니다.')
        return file


class RegulationSearchForm(forms.Form):
    """사규 검색 폼"""
    
    keyword = forms.CharField(
        label='검색어',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '사규명 또는 사규코드 검색'
        })
    )
    category = forms.ChoiceField(
        label='분류',
        required=False,
        choices=[('', '전체')] + Regulation.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        label='상태',
        required=False,
        choices=[('', '전체')] + Regulation.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_mandatory = forms.ChoiceField(
        label='의무준수',
        required=False,
        choices=[('', '전체'), ('true', '의무'), ('false', '비의무')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    responsible_dept = forms.IntegerField(
        label='책임부서',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )






