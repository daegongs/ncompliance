"""
사규 관리 뷰
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy, reverse
from django.http import FileResponse, Http404, JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Regulation, RegulationVersion, RegulationTag, RegulationDownloadLog
from .forms import RegulationForm, RegulationVersionForm, RegulationSearchForm
from accounts.models import Department


class RegulationListView(LoginRequiredMixin, ListView):
    """사규 목록 뷰"""

    model = Regulation
    template_name = "regulations/regulation_list.html"
    context_object_name = "regulations"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        queryset = Regulation.objects.accessible_to(user).select_related(
            "responsible_dept"
        )
        
        # 책임부서담당(DEPT_MANAGER)인 경우: 자신이 담당하는 사규만 표시
        # 자신의 부서가 책임부서인 사규 또는 자신이 담당자/책임자로 지정된 사규
        if user.role == 'DEPT_MANAGER' and user.department:
            queryset = queryset.filter(
                Q(responsible_dept=user.department) |
                Q(manager__icontains=user.get_full_name()) |
                Q(manager_primary__icontains=user.get_full_name())
            )

        # 검색 필터 적용
        keyword = self.request.GET.get("keyword", "").strip()
        category = self.request.GET.get("category", "")
        status = self.request.GET.get("status", "")
        is_mandatory = self.request.GET.get("is_mandatory", "")
        responsible_dept = self.request.GET.get("responsible_dept", "")
        group = self.request.GET.get("group", "").strip()
        manager = self.request.GET.get("manager", "").strip()
        is_public = self.request.GET.get("is_public", "")

        if keyword:
            queryset = queryset.filter(
                Q(code__icontains=keyword)
                | Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(manager__icontains=keyword)
                | Q(group__icontains=keyword)
            )

        if category:
            queryset = queryset.filter(category=category)

        if status:
            queryset = queryset.filter(status=status)

        # 의무준수 필터: mandatory(의무), non_mandatory(비의무), not_applicable(사규관리 비대상)
        if is_mandatory:
            if is_mandatory == "mandatory":
                queryset = queryset.filter(is_mandatory=True)
            elif is_mandatory == "non_mandatory":
                queryset = queryset.filter(is_mandatory=False).exclude(scope='NOT_APPLICABLE')
            elif is_mandatory == "not_applicable":
                # 사규관리 비대상: is_mandatory=False이면서 별도 표시된 것들
                queryset = queryset.filter(is_mandatory=False)

        if responsible_dept:
            queryset = queryset.filter(responsible_dept_id=responsible_dept)

        if group:
            queryset = queryset.filter(group__icontains=group)

        if manager:
            queryset = queryset.filter(manager__icontains=manager)

        # 임직원 공개 필터: all(전체공개), executive(임원공개), private(비공개)
        if is_public:
            if is_public == "all":
                queryset = queryset.filter(is_public=True, access_level='ALL')
            elif is_public == "executive":
                queryset = queryset.filter(is_public=True).exclude(access_level='ALL')
            elif is_public == "private":
                queryset = queryset.filter(is_public=False)

        return queryset.order_by("category", "code")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = RegulationSearchForm(self.request.GET)
        context["departments"] = Department.objects.filter(is_active=True)
        context["total_count"] = self.get_queryset().count()
        context["is_dept_manager"] = self.request.user.role == 'DEPT_MANAGER'

        # 분류별 카운트 (권한 적용)
        context["category_counts"] = (
            Regulation.objects.accessible_to(self.request.user)
            .values("category")
            .annotate(count=Count("id"))
        )

        return context


class CategoryRegulationListView(RegulationListView):
    """카테고리별 사규 목록 뷰"""

    def get_queryset(self):
        category_code = self.kwargs.get("category").upper()
        return super().get_queryset().filter(category=category_code)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_code = self.kwargs.get("category").upper()
        category_display = dict(Regulation.CATEGORY_CHOICES).get(
            category_code, category_code
        )
        context["category_display"] = category_display
        context["is_category_view"] = True
        return context


class RegulationDetailView(LoginRequiredMixin, DetailView):
    """사규 상세 뷰"""

    model = Regulation
    template_name = "regulations/regulation_detail.html"
    context_object_name = "regulation"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # 접근 권한 체크
        if not self.object.can_user_access(request.user):
            messages.error(request, "이 사규에 대한 접근 권한이 없습니다.")
            return redirect("regulations:list")
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["versions"] = self.object.versions.all().order_by("-created_at")
        context["related"] = self.object.related_regulations.all()
        context["children"] = self.object.child_regulations.all()
        return context


class RegulationCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """사규 등록 뷰"""

    model = Regulation
    form_class = RegulationForm
    template_name = "regulations/regulation_form.html"

    def test_func(self):
        """사규 등록 권한 확인"""
        return self.request.user.can_manage_regulations()

    def get_initial(self):
        """책임부서담당자인 경우 기본값 설정"""
        initial = super().get_initial()
        user = self.request.user
        
        # 책임부서담당(DEPT_MANAGER)인 경우: 부서와 담당자 기본값 설정
        if user.role == 'DEPT_MANAGER':
            if user.department:
                initial['responsible_dept'] = user.department
            initial['manager'] = user.get_full_name()
        
        return initial

    def get_form(self, form_class=None):
        """책임부서담당자인 경우 필드 제한"""
        form = super().get_form(form_class)
        user = self.request.user
        
        # 책임부서담당(DEPT_MANAGER)인 경우: 책임부서 필드를 읽기 전용으로
        if user.role == 'DEPT_MANAGER' and user.department:
            form.fields['responsible_dept'].widget.attrs['readonly'] = True
            form.fields['responsible_dept'].widget.attrs['disabled'] = True
            # disabled 필드는 POST에서 제외되므로 hidden으로도 전달 필요
            form.fields['responsible_dept'].required = False
        
        return form

    def form_valid(self, form):
        user = self.request.user
        form.instance.created_by = user
        form.instance.status = "ACTIVE"
        
        # DEPT_MANAGER인 경우: 책임부서를 강제로 자신의 부서로 설정
        if user.role == 'DEPT_MANAGER' and user.department:
            form.instance.responsible_dept = user.department
        
        messages.success(self.request, "사규가 등록되었습니다.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("regulations:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = True
        context["title"] = "사규 등록"
        context["is_dept_manager"] = self.request.user.role == 'DEPT_MANAGER'
        return context


class RegulationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """사규 수정 뷰"""

    model = Regulation
    form_class = RegulationForm
    template_name = "regulations/regulation_form.html"

    def test_func(self):
        """사규 수정 권한 확인"""
        user = self.request.user
        if not user.can_manage_regulations():
            return False
        
        # DEPT_MANAGER는 자신의 부서 사규만 수정 가능
        if user.role == 'DEPT_MANAGER':
            regulation = self.get_object()
            if regulation.responsible_dept != user.department:
                return False
        
        return True

    def get_form(self, form_class=None):
        """책임부서담당자인 경우 필드 제한"""
        form = super().get_form(form_class)
        user = self.request.user
        
        # 책임부서담당(DEPT_MANAGER)인 경우: 책임부서 변경 불가
        if user.role == 'DEPT_MANAGER' and user.department:
            form.fields['responsible_dept'].widget.attrs['readonly'] = True
            form.fields['responsible_dept'].widget.attrs['disabled'] = True
            form.fields['responsible_dept'].required = False
        
        return form

    def form_valid(self, form):
        user = self.request.user
        
        # DEPT_MANAGER인 경우: 책임부서 변경 방지
        if user.role == 'DEPT_MANAGER' and user.department:
            form.instance.responsible_dept = user.department
        
        messages.success(self.request, "사규가 수정되었습니다.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("regulations:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = False
        context["title"] = "사규 수정"
        context["is_dept_manager"] = self.request.user.role == 'DEPT_MANAGER'
        return context


class RegulationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """사규 삭제 뷰"""

    model = Regulation
    template_name = "regulations/regulation_confirm_delete.html"
    success_url = reverse_lazy("regulations:list")

    def test_func(self):
        """사규 삭제 권한 확인 (관리자만)"""
        return self.request.user.role in ["COMPLIANCE", "ADMIN"]

    def delete(self, request, *args, **kwargs):
        messages.success(request, "사규가 삭제되었습니다.")
        return super().delete(request, *args, **kwargs)


class RegulationVersionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """사규 버전 등록 뷰"""

    model = RegulationVersion
    form_class = RegulationVersionForm
    template_name = "regulations/version_form.html"

    def test_func(self):
        return self.request.user.can_manage_regulations()

    def dispatch(self, request, *args, **kwargs):
        self.regulation = get_object_or_404(Regulation, pk=kwargs["regulation_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.regulation = self.regulation
        form.instance.created_by = self.request.user

        # 제정인 경우에만 사규 상태를 시행중으로 변경
        if form.instance.change_type == "CREATE":
            self.regulation.status = "ACTIVE"
            self.regulation.current_version = form.instance.version_number
            self.regulation.save()
        # 개정인 경우 버전 업데이트
        elif form.instance.change_type == "REVISE":
            self.regulation.current_version = form.instance.version_number
            self.regulation.save()
        # 폐지인 경우
        elif form.instance.change_type == "ABOLISH":
            self.regulation.status = "ABOLISHED"
            self.regulation.abolished_date = timezone.now().date()
            self.regulation.save()

        messages.success(self.request, "버전이 등록되었습니다.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("regulations:detail", kwargs={"pk": self.regulation.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["regulation"] = self.regulation
        context["latest_version"] = self.regulation.get_latest_version()
        return context


@login_required
def download_regulation_file(request, version_pk):
    """사규 파일 다운로드"""
    version = get_object_or_404(RegulationVersion, pk=version_pk)

    if not version.content_file:
        raise Http404("첨부파일이 없습니다.")

    # 다운로드 로그 기록
    RegulationDownloadLog.objects.create(
        regulation=version.regulation,
        version=version,
        user=request.user,
        ip_address=request.META.get("REMOTE_ADDR"),
    )

    # 파일 응답
    response = FileResponse(
        version.content_file.open("rb"),
        as_attachment=True,
        filename=version.content_file.name.split("/")[-1],
    )
    return response


@login_required
def regulation_history(request, pk):
    """사규 변경 이력 조회"""
    regulation = get_object_or_404(Regulation, pk=pk)
    versions = regulation.versions.all().order_by("-created_at")

    return render(
        request,
        "regulations/regulation_history.html",
        {
            "regulation": regulation,
            "versions": versions,
        },
    )


@login_required
def tag_list(request):
    """태그 목록"""
    user = request.user
    
    # 책임부서담당자(DEPT_MANAGER)인 경우: 자신이 담당하는 사규의 태그만 표시
    if user.role == 'DEPT_MANAGER' and user.department:
        # 자신의 부서가 책임부서인 사규 또는 자신이 담당자로 지정된 사규의 태그
        my_regulations = Regulation.objects.filter(
            Q(responsible_dept=user.department) |
            Q(manager__icontains=user.get_full_name()) |
            Q(manager_primary__icontains=user.get_full_name())
        )
        tags = RegulationTag.objects.filter(
            regulations__in=my_regulations
        ).distinct().annotate(
            regulation_count=Count("regulations", filter=Q(regulations__in=my_regulations))
        ).order_by("-regulation_count")
        total_regulations = my_regulations.count()
    else:
        # 다른 권한은 모든 태그 표시
        tags = RegulationTag.objects.annotate(
            regulation_count=Count("regulations")
        ).order_by("-regulation_count")
        total_regulations = Regulation.objects.count()

    return render(
        request,
        "regulations/tag_list.html",
        {
            "tags": tags,
            "is_dept_manager": user.role == 'DEPT_MANAGER',
            "total_regulations": total_regulations,
        },
    )


@login_required
def regulations_by_tag(request, tag_name):
    """태그별 사규 목록"""
    user = request.user
    tag = get_object_or_404(RegulationTag, name=tag_name)
    
    # 책임부서담당자(DEPT_MANAGER)인 경우: 자신이 담당하는 사규만 표시
    if user.role == 'DEPT_MANAGER' and user.department:
        regulations = tag.regulations.filter(
            Q(responsible_dept=user.department) |
            Q(manager__icontains=user.get_full_name()) |
            Q(manager_primary__icontains=user.get_full_name())
        )
    else:
        regulations = tag.regulations.all()

    return render(
        request,
        "regulations/regulations_by_tag.html",
        {
            "tag": tag,
            "regulations": regulations,
        },
    )


@login_required
def get_regulations_by_category(request):
    """카테고리별 사규 목록을 JSON으로 반환 (AJAX)"""
    category = request.GET.get("category", "")
    exclude_pk = request.GET.get("exclude_pk", "")

    queryset = Regulation.objects.all()

    if category:
        queryset = queryset.filter(category=category)

    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)

    regulations = queryset.values("id", "code", "title", "category")

    return JsonResponse({"regulations": list(regulations)})


# ============================================
# 공통코드 관리 뷰
# ============================================

from .models import CommonCode


def is_admin(user):
    """관리자 여부 확인"""
    return user.is_superuser or (hasattr(user, 'role') and user.role == 'ADMIN')


@login_required
def code_list(request):
    """공통코드 목록"""
    if not is_admin(request.user):
        messages.error(request, "관리자만 접근할 수 있습니다.")
        return redirect("dashboard:index")
    
    code_type = request.GET.get("code_type", "")
    is_active = request.GET.get("is_active", "")
    keyword = request.GET.get("keyword", "").strip()
    
    codes = CommonCode.objects.all()
    
    if code_type:
        codes = codes.filter(code_type=code_type)
    
    if is_active == "true":
        codes = codes.filter(is_active=True)
    elif is_active == "false":
        codes = codes.filter(is_active=False)
    
    if keyword:
        codes = codes.filter(
            Q(code__icontains=keyword) | 
            Q(name__icontains=keyword) | 
            Q(description__icontains=keyword)
        )
    
    codes = codes.order_by("code_type", "sort_order", "code")
    
    # 코드 유형별 그룹화
    grouped_codes = {}
    for code in codes:
        code_type_display = code.get_code_type_display()
        if code_type_display not in grouped_codes:
            grouped_codes[code_type_display] = []
        grouped_codes[code_type_display].append(code)
    
    return render(request, "regulations/code_list.html", {
        "codes": codes,
        "grouped_codes": grouped_codes,
        "code_type_choices": CommonCode.CODE_TYPE_CHOICES,
        "current_code_type": code_type,
        "current_is_active": is_active,
        "keyword": keyword,
    })


@login_required
def code_create(request):
    """공통코드 등록"""
    if not is_admin(request.user):
        messages.error(request, "관리자만 접근할 수 있습니다.")
        return redirect("dashboard:index")
    
    if request.method == "POST":
        code_type = request.POST.get("code_type")
        code = request.POST.get("code", "").strip()
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        sort_order = request.POST.get("sort_order", 0)
        is_active = request.POST.get("is_active") == "on"
        
        if not code_type or not code or not name:
            messages.error(request, "코드유형, 코드, 코드명은 필수 입력 항목입니다.")
            return redirect("regulations:code_create")
        
        # 중복 체크
        if CommonCode.objects.filter(code_type=code_type, code=code).exists():
            messages.error(request, f"동일한 코드유형에 '{code}' 코드가 이미 존재합니다.")
            return redirect("regulations:code_create")
        
        CommonCode.objects.create(
            code_type=code_type,
            code=code,
            name=name,
            description=description,
            sort_order=int(sort_order) if sort_order else 0,
            is_active=is_active,
        )
        
        messages.success(request, f"코드 '{name}'이(가) 등록되었습니다.")
        return redirect("regulations:code_list")
    
    return render(request, "regulations/code_form.html", {
        "code_type_choices": CommonCode.CODE_TYPE_CHOICES,
        "is_create": True,
    })


@login_required
def code_update(request, pk):
    """공통코드 수정"""
    if not is_admin(request.user):
        messages.error(request, "관리자만 접근할 수 있습니다.")
        return redirect("dashboard:index")
    
    code_obj = get_object_or_404(CommonCode, pk=pk)
    
    if request.method == "POST":
        code_obj.code_type = request.POST.get("code_type")
        code_obj.code = request.POST.get("code", "").strip()
        code_obj.name = request.POST.get("name", "").strip()
        code_obj.description = request.POST.get("description", "").strip()
        code_obj.sort_order = int(request.POST.get("sort_order", 0) or 0)
        code_obj.is_active = request.POST.get("is_active") == "on"
        
        if not code_obj.code_type or not code_obj.code or not code_obj.name:
            messages.error(request, "코드유형, 코드, 코드명은 필수 입력 항목입니다.")
            return redirect("regulations:code_update", pk=pk)
        
        # 중복 체크 (자신 제외)
        if CommonCode.objects.filter(
            code_type=code_obj.code_type, 
            code=code_obj.code
        ).exclude(pk=pk).exists():
            messages.error(request, f"동일한 코드유형에 '{code_obj.code}' 코드가 이미 존재합니다.")
            return redirect("regulations:code_update", pk=pk)
        
        code_obj.save()
        messages.success(request, f"코드 '{code_obj.name}'이(가) 수정되었습니다.")
        return redirect("regulations:code_list")
    
    return render(request, "regulations/code_form.html", {
        "code_obj": code_obj,
        "code_type_choices": CommonCode.CODE_TYPE_CHOICES,
        "is_create": False,
    })


@login_required
def code_delete(request, pk):
    """공통코드 삭제"""
    if not is_admin(request.user):
        messages.error(request, "관리자만 접근할 수 있습니다.")
        return redirect("dashboard:index")
    
    code_obj = get_object_or_404(CommonCode, pk=pk)
    
    if code_obj.is_system:
        messages.error(request, f"시스템 코드 '{code_obj.name}'은(는) 삭제할 수 없습니다.")
        return redirect("regulations:code_list")
    
    if request.method == "POST":
        name = code_obj.name
        code_obj.delete()
        messages.success(request, f"코드 '{name}'이(가) 삭제되었습니다.")
        return redirect("regulations:code_list")
    
    return render(request, "regulations/code_confirm_delete.html", {
        "code_obj": code_obj,
    })
