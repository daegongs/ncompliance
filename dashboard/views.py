"""
대시보드 뷰
사규 현황 및 통계를 보여주는 메인 대시보드
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta

from regulations.models import Regulation, RegulationVersion, Favorite


@login_required
def index(request):
    """메인 대시보드 - 트리 구조 브라우징"""
    # 권한이 필터링된 기본 쿼리셋
    accessible_regulations = Regulation.objects.accessible_to(request.user).select_related("responsible_dept")
    
    # 관리자/준법지원인은 모든 사규 조회 가능 (비공개 포함)
    # 일반 사용자는 비공개(is_public=False), 사규관리 비대상(is_mandatory=False) 제외
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'role') and request.user.role in ['ADMIN', 'COMPLIANCE']
    )
    
    if not is_admin:
        accessible_regulations = accessible_regulations.filter(
            is_public=True,
            is_mandatory=True
        )

    # 전체 사규 수 (매뉴얼/가이드라인 제외)
    total_regulations = accessible_regulations.exclude(category='MANUAL').count()

    # 카테고리 필터 (매뉴얼/가이드라인 제외)
    current_category = request.GET.get("category", "")
    if current_category:
        filtered_regulations = accessible_regulations.filter(category=current_category)
    else:
        # 매뉴얼/가이드라인(MANUAL) 제외
        filtered_regulations = accessible_regulations.exclude(category='MANUAL')

    # 분류별 카운트
    category_counts = {
        'POLICY': accessible_regulations.filter(category='POLICY').count(),
        'REGULATION': accessible_regulations.filter(category='REGULATION').count(),
        'GUIDELINE': accessible_regulations.filter(category='GUIDELINE').count(),
        'MANUAL': accessible_regulations.filter(category='MANUAL').count(),
    }

    # 사용자의 즐겨찾기 목록 가져오기
    favorite_regulation_ids = set(
        Favorite.objects.filter(user=request.user).values_list('regulation_id', flat=True)
    )

    # 즐겨찾기된 사규 필터링 (현재 카테고리 조건 적용)
    favorite_regulations = filtered_regulations.filter(pk__in=favorite_regulation_ids)

    # 그룹 → 카테고리 순서로 사규 정리 (트리 구조용, 매뉴얼/가이드라인 제외)
    grouped_regulations = {}
    category_order = ['POLICY', 'REGULATION', 'GUIDELINE']

    # 그룹 노출 순서 정의
    group_order = [
        '이사회', 'HR', '재무', '구매', '준법', '반부패', 
        '정보보호', '개인정보보호', '안전보건', 'ESG'
    ]

    for reg in filtered_regulations:
        cat = reg.category
        grp = reg.group or '(그룹 없음)'

        if grp not in grouped_regulations:
            grouped_regulations[grp] = {}
        if cat not in grouped_regulations[grp]:
            grouped_regulations[grp][cat] = []
        grouped_regulations[grp][cat].append(reg)

    # 그룹 커스텀 순서로 정렬 (지정된 순서 우선, 나머지는 알파벳순)
    def get_group_sort_key(grp_name):
        # '(그룹 없음)'은 맨 마지막에 표시
        if grp_name == '(그룹 없음)':
            return (999, grp_name)
        # 지정된 순서에 있으면 해당 인덱스 반환, 없으면 큰 숫자 + 알파벳순
        for i, g in enumerate(group_order):
            if g in grp_name or grp_name in g:
                return (i, grp_name)
        return (len(group_order), grp_name)
    
    sorted_groups = sorted(grouped_regulations.keys(), key=get_group_sort_key)

    # (그룹명, 카테고리별 사규, 총건수) 리스트로 구성
    grouped_list = []
    
    # 즐겨찾기 그룹 먼저 추가 (맨 위)
    if favorite_regulations.exists():
        fav_categories_dict = {}
        fav_total = 0
        for cat in category_order:
            cat_regs = [r for r in favorite_regulations if r.category == cat]
            if cat_regs:
                fav_categories_dict[cat] = sorted(cat_regs, key=lambda x: x.title)
                fav_total += len(cat_regs)
        
        if fav_total > 0:
            grouped_list.append({
                'name': '즐겨찾기',
                'categories': fav_categories_dict,
                'total': fav_total,
                'is_favorite_group': True
            })
    
    # 나머지 그룹 추가
    for grp_name in sorted_groups:
        categories_dict = {}
        total = 0
        for cat in category_order:
            if cat in grouped_regulations[grp_name]:
                # 각 카테고리 내 사규는 제목순 정렬
                categories_dict[cat] = sorted(
                    grouped_regulations[grp_name][cat],
                    key=lambda x: x.title
                )
                total += len(grouped_regulations[grp_name][cat])
        grouped_list.append({
            'name': grp_name,
            'categories': categories_dict,
            'total': total,
            'is_favorite_group': False
        })

    context = {
        "total_count": total_regulations,
        "category_counts": category_counts,
        "current_category": current_category,
        "grouped_regulations": grouped_list,
        "category_choices": Regulation.CATEGORY_CHOICES,
        "favorite_regulation_ids": list(favorite_regulation_ids),
    }

    return render(request, "dashboard/index.html", context)


def landing(request):
    """랜딩 페이지 (로그인 전)"""
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    return redirect("accounts:login")


@login_required
def regulation_content(request, pk):
    """사규 본문 API - JSON으로 반환"""
    regulation = get_object_or_404(Regulation, pk=pk)
    
    # 즐겨찾기 여부 확인
    is_favorite = Favorite.objects.filter(
        user=request.user, regulation=regulation
    ).exists()
    
    return JsonResponse({
        'id': regulation.pk,
        'title': regulation.title,
        'content': regulation.content or '',
        'reference_url': regulation.reference_url or '',
        'category': regulation.get_category_display(),
        'group': regulation.group or '',
        'manager': regulation.manager or '',
        'responsible_dept': regulation.responsible_dept.name if regulation.responsible_dept else '',
        'is_favorite': is_favorite,
    })


@login_required
@require_POST
def toggle_favorite(request, pk):
    """즐겨찾기 토글 API"""
    regulation = get_object_or_404(Regulation, pk=pk)
    
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        regulation=regulation
    )
    
    if not created:
        # 이미 존재하면 삭제 (즐겨찾기 해제)
        favorite.delete()
        return JsonResponse({
            'status': 'removed',
            'is_favorite': False,
            'message': '즐겨찾기가 해제되었습니다.'
        })
    
    return JsonResponse({
        'status': 'added',
        'is_favorite': True,
        'message': '즐겨찾기에 추가되었습니다.'
    })
