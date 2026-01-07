"""
사규 관련 모델
Regulation models for nCompliance
"""

import os
from django.db import models
from django.conf import settings


def regulation_file_path(instance, filename):
    """사규 파일 저장 경로 생성"""
    ext = filename.split(".")[-1]
    filename = f"{instance.regulation.code}_v{instance.version_number}.{ext}"
    return os.path.join("regulations", instance.regulation.code, filename)


class RegulationQuerySet(models.QuerySet):
    """사규 검색 및 권한 필터링을 위한 쿼리셋"""

    def accessible_to(self, user):
        # 관리자/준법지원인은 전체 접근 가능
        if user.is_superuser or (
            hasattr(user, "role") and user.role in ["ADMIN", "COMPLIANCE"]
        ):
            return self

        # access_level이 'ALL'인 사규는 모든 사용자에게 공개
        # 부서별/직원별 권한은 해당 조건 충족 시 공개
        access_filter = models.Q(access_level="ALL")

        # 부서별 접근 권한
        if hasattr(user, "department") and user.department:
            access_filter |= models.Q(
                access_level="DEPARTMENTS", allowed_departments=user.department
            )

            # 책임부서 담당자는 자신 부서의 사규 항상 접근 가능
            if hasattr(user, "role") and user.role == "DEPT_MANAGER":
                access_filter |= models.Q(responsible_dept=user.department)

        # 직원별 접근 권한
        access_filter |= models.Q(access_level="USERS", allowed_users=user)

        return self.filter(access_filter).distinct()


class Regulation(models.Model):
    """
    사규 모델
    회사의 모든 사규(정책, 규정, 지침 등)를 관리하는 핵심 모델
    """

    objects = RegulationQuerySet.as_manager()

    CATEGORY_CHOICES = [
        ("POLICY", "정책/방침"),
        ("REGULATION", "규정"),
        ("GUIDELINE", "지침"),
        ("MANUAL", "매뉴얼/가이드라인"),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", "시행중"),
        ("ABOLISHED", "폐지"),
    ]

    SCOPE_CHOICES = [
        ("ALL", "전 임직원"),
        ("DEPT", "소속부서"),
    ]

    ACCESS_LEVEL_CHOICES = [
        ("ALL", "전체 직원"),
        ("DEPARTMENTS", "지정된 부서"),
        ("USERS", "지정된 직원"),
    ]

    code = models.CharField("사규코드", max_length=20, unique=True)
    title = models.CharField("사규명", max_length=200)
    category = models.CharField("분류", max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField("설명", blank=True)

    is_mandatory = models.BooleanField("의무준수", default=True)
    scope = models.CharField(
        "적용범위", max_length=10, choices=SCOPE_CHOICES, default="ALL"
    )
    status = models.CharField(
        "상태", max_length=20, choices=STATUS_CHOICES, default="ACTIVE"
    )

    responsible_dept = models.ForeignKey(
        "accounts.Department",
        on_delete=models.PROTECT,
        related_name="regulations",
        verbose_name="책임부서",
    )
    manager = models.CharField(
        "사규관리 담당자", max_length=100, blank=True, help_text="사규관리 담당자 이름"
    )
    manager_primary = models.CharField(
        "사규관리 책임자", max_length=100, blank=True, help_text="사규관리 책임자 이름"
    )
    group = models.CharField(
        "그룹", max_length=100, blank=True, help_text="소속 그룹 또는 조직"
    )

    current_version = models.CharField("현재버전", max_length=10, default="1.0")
    effective_date = models.DateField("시행일", null=True, blank=True)
    expiry_date = models.DateField("정기검토예정일", null=True, blank=True)
    abolished_date = models.DateField("폐지일", null=True, blank=True)

    parent_regulation = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_regulations",
        verbose_name="상위사규",
    )
    related_regulations = models.ManyToManyField(
        "self", blank=True, symmetrical=False, verbose_name="관련사규"
    )

    # 접근 권한
    access_level = models.CharField(
        "접근 권한",
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        default="ALL",
        help_text="사규 접근 권한 설정",
    )
    allowed_companies = models.ManyToManyField(
        "accounts.Company",
        blank=True,
        related_name="accessible_regulations",
        verbose_name="허용된 법인",
    )
    allowed_departments = models.ManyToManyField(
        "accounts.Department",
        blank=True,
        related_name="accessible_regulations",
        verbose_name="허용된 부서",
    )
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="accessible_regulations",
        verbose_name="허용된 직원",
    )

    is_public = models.BooleanField(
        "임직원 공개", default=True, help_text="임직원에게 공개 여부"
    )
    reference_url = models.URLField(
        "참조링크", null=True, blank=True, help_text="사규 원문 링크"
    )
    content = models.TextField(
        "규정 본문", blank=True, help_text="사규의 본문 내용"
    )
    original_file = models.FileField(
        "사규 원본 파일",
        upload_to="regulations/original/",
        null=True,
        blank=True,
        help_text="사규 원본 파일 (PDF, Word, HWP 등)"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_regulations",
        verbose_name="작성자",
    )
    created_at = models.DateTimeField("생성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        verbose_name = "사규"
        verbose_name_plural = "사규"
        ordering = ["category", "code"]

    def __str__(self):
        return f"[{self.code}] {self.title}"

    def get_category_display_class(self):
        """카테고리에 따른 Bootstrap badge 클래스 반환"""
        category_classes = {
            'POLICY': 'bg-primary text-white',
            'REGULATION': 'bg-info text-dark',
            'GUIDELINE': 'bg-success text-white',
            'MANUAL': 'bg-warning text-dark',
        }
        return category_classes.get(self.category, 'bg-secondary text-white')

    def get_latest_version(self):
        """최신 버전 객체 반환"""
        return self.versions.order_by("-created_at").first()

    def can_user_access(self, user):
        """사용자의 사규 접근 권한 확인"""
        if user.is_superuser or (
            hasattr(user, "role") and user.role in ["ADMIN", "COMPLIANCE"]
        ):
            return True

        # 법인 확인
        user_company = getattr(user, "company", None) or (
            user.department.company
            if hasattr(user, "department") and user.department
            else None
        )
        if (
            not user_company
            or not self.allowed_companies.all().filter(pk=user_company.pk).exists()
        ):
            return False

        # 책임부서 담당자는 항상 접근 가능 (법인 일치 확인됨)
        if user.role == "DEPT_MANAGER" and user.department == self.responsible_dept:
            return True

        if self.access_level == "ALL":
            return True
        elif self.access_level == "DEPARTMENTS":
            return (
                self.allowed_departments.filter(pk=user.department.pk).exists()
                if user.department
                else False
            )
        elif self.access_level == "USERS":
            return self.allowed_users.filter(pk=user.pk).exists()

        return False

    @staticmethod
    def generate_code(category):
        """카테고리에 따른 사규코드 자동 생성"""
        prefix = {
            "POLICY": "POL",
            "REGULATION": "REG",
            "GUIDELINE": "GUI",
            "MANUAL": "MAN",
        }.get(category, "OTH")

        last_reg = (
            Regulation.objects.filter(category=category).order_by("-code").first()
        )
        if last_reg and last_reg.code.startswith(prefix):
            try:
                last_num = int(last_reg.code[len(prefix) :])
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"


class RegulationVersion(models.Model):
    """
    사규 버전 모델
    사규의 제정, 개정 이력을 관리
    """

    CHANGE_TYPE_CHOICES = [
        ("CREATE", "제정"),
        ("REVISE", "개정"),
        ("ABOLISH", "폐지"),
    ]

    regulation = models.ForeignKey(
        Regulation,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name="사규",
    )
    version_number = models.CharField("버전번호", max_length=10)
    change_type = models.CharField(
        "변경유형", max_length=10, choices=CHANGE_TYPE_CHOICES
    )
    change_reason = models.TextField("변경사유")
    change_summary = models.TextField("변경내용요약", blank=True)
    content_file = models.FileField(
        "첨부파일", upload_to=regulation_file_path, null=True, blank=True
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_versions",
        verbose_name="승인자",
    )
    approved_at = models.DateTimeField("승인일", null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_versions",
        verbose_name="작성자",
    )
    created_at = models.DateTimeField("생성일", auto_now_add=True)

    class Meta:
        verbose_name = "사규 버전"
        verbose_name_plural = "사규 버전"
        ordering = ["-created_at"]
        unique_together = ["regulation", "version_number"]

    def __str__(self):
        return f"{self.regulation.code} v{self.version_number}"


class RegulationTag(models.Model):
    """
    사규 태그 모델
    """

    name = models.CharField("태그명", max_length=50, unique=True)
    regulations = models.ManyToManyField(
        Regulation, blank=True, related_name="tags", verbose_name="사규"
    )
    created_at = models.DateTimeField("생성일", auto_now_add=True)

    class Meta:
        verbose_name = "태그"
        verbose_name_plural = "태그"
        ordering = ["name"]

    def __str__(self):
        return self.name


class RegulationDownloadLog(models.Model):
    """
    사규 다운로드 로그
    사후 통제 및 감사 추적용
    """

    regulation = models.ForeignKey(
        Regulation,
        on_delete=models.CASCADE,
        related_name="download_logs",
        verbose_name="사규",
    )
    version = models.ForeignKey(
        RegulationVersion,
        on_delete=models.CASCADE,
        related_name="download_logs",
        verbose_name="버전",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="download_logs",
        verbose_name="사용자",
    )
    ip_address = models.GenericIPAddressField("IP 주소", null=True, blank=True)
    downloaded_at = models.DateTimeField("다운로드일시", auto_now_add=True)

    class Meta:
        verbose_name = "다운로드 로그"
        verbose_name_plural = "다운로드 로그"
        ordering = ["-downloaded_at"]

    def __str__(self):
        return f"{self.user} download {self.regulation} at {self.downloaded_at}"


class Approval(models.Model):
    """
    결재 모델
    사규의 제개정 승인 프로세스 관리
    """

    STATUS_CHOICES = [
        ("PENDING", "결재대기"),
        ("APPROVING", "결재중"),
        ("APPROVED", "승인완료"),
        ("REJECTED", "반려"),
        ("CANCELLED", "취소"),
    ]

    regulation = models.OneToOneField(
        Regulation,
        on_delete=models.CASCADE,
        related_name="approval",
        verbose_name="사규",
    )
    status = models.CharField(
        "결재상태", max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )
    request_reason = models.TextField(
        "결재사유", help_text="결재를 요청하는 사유를 입력하세요"
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="requested_approvals",
        verbose_name="요청자",
    )
    requested_at = models.DateTimeField("요청일시", auto_now_add=True)
    completed_at = models.DateTimeField("완료일시", null=True, blank=True)
    rejection_reason = models.TextField(
        "반려사유", blank=True, help_text="반려 시 사유를 입력하세요"
    )

    class Meta:
        verbose_name = "결재"
        verbose_name_plural = "결재"
        ordering = ["-requested_at"]

    def __str__(self):
        return f"Approval for {self.regulation.title}"


class ApprovalLine(models.Model):
    """
    결재 라인 모델
    단계별 결재자 지정 및 상태 관리
    """

    STATUS_CHOICES = [
        ("PENDING", "대기"),
        ("APPROVED", "승인"),
        ("REJECTED", "반려"),
    ]

    approval = models.ForeignKey(
        Approval,
        on_delete=models.CASCADE,
        related_name="approval_lines",
        verbose_name="결재",
    )
    sequence = models.IntegerField("순서", help_text="결재 순서 (1부터 시작)")
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="approval_lines",
        verbose_name="결재자",
    )
    role_name = models.CharField(
        "역할명",
        max_length=50,
        blank=True,
        help_text="결재자의 역할 (예: 부문장, 준법지원인)",
    )
    status = models.CharField(
        "상태", max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )
    comment = models.TextField("의견", blank=True)
    approved_at = models.DateTimeField("결재일시", null=True, blank=True)

    class Meta:
        verbose_name = "결재 라인"
        verbose_name_plural = "결재 라인"
        ordering = ["approval", "sequence"]
        unique_together = ["approval", "sequence"]

    def __str__(self):
        return f"Line {self.sequence} for {self.approval}"


class Favorite(models.Model):
    """
    즐겨찾기 모델
    사용자별 사규 즐겨찾기 관리
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="사용자",
    )
    regulation = models.ForeignKey(
        Regulation,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="사규",
    )
    created_at = models.DateTimeField("생성일", auto_now_add=True)

    class Meta:
        verbose_name = "즐겨찾기"
        verbose_name_plural = "즐겨찾기"
        ordering = ["-created_at"]
        unique_together = ["user", "regulation"]

    def __str__(self):
        return f"{self.user} - {self.regulation.title}"


class CommonCode(models.Model):
    """
    공통 코드 모델
    사규 관리에 필요한 코드 정보를 관리
    """

    CODE_TYPE_CHOICES = [
        ("GROUP", "그룹"),
        ("CATEGORY", "분류"),
        ("STATUS", "상태"),
        ("SCOPE", "적용범위"),
        ("ACCESS_LEVEL", "접근권한"),
        ("CHANGE_TYPE", "변경유형"),
        ("CUSTOM", "사용자정의"),
    ]

    code_type = models.CharField(
        "코드유형",
        max_length=20,
        choices=CODE_TYPE_CHOICES,
        help_text="코드의 유형을 선택하세요"
    )
    code = models.CharField(
        "코드",
        max_length=50,
        help_text="시스템에서 사용되는 코드 값"
    )
    name = models.CharField(
        "코드명",
        max_length=100,
        help_text="화면에 표시되는 이름"
    )
    description = models.TextField(
        "설명",
        blank=True,
        help_text="코드에 대한 상세 설명"
    )
    sort_order = models.IntegerField(
        "정렬순서",
        default=0,
        help_text="목록 표시 순서 (작은 숫자가 먼저 표시)"
    )
    is_active = models.BooleanField(
        "사용여부",
        default=True,
        help_text="체크 해제 시 선택 목록에서 숨김"
    )
    is_system = models.BooleanField(
        "시스템코드",
        default=False,
        help_text="시스템 코드는 삭제할 수 없습니다"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="상위코드",
        help_text="계층 구조가 필요한 경우 상위 코드 지정"
    )
    created_at = models.DateTimeField("생성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        verbose_name = "공통코드"
        verbose_name_plural = "공통코드"
        ordering = ["code_type", "sort_order", "code"]
        unique_together = ["code_type", "code"]

    def __str__(self):
        return f"[{self.get_code_type_display()}] {self.name}"

    @classmethod
    def get_codes(cls, code_type, active_only=True):
        """특정 유형의 코드 목록 반환"""
        queryset = cls.objects.filter(code_type=code_type)
        if active_only:
            queryset = queryset.filter(is_active=True)
        return queryset.order_by("sort_order", "name")

    @classmethod
    def get_choices(cls, code_type, active_only=True):
        """특정 유형의 코드를 choices 형식으로 반환"""
        codes = cls.get_codes(code_type, active_only)
        return [(c.code, c.name) for c in codes]
