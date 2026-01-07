"""
사규 관리 URL 설정
"""

from django.urls import path
from . import views

app_name = "regulations"

urlpatterns = [
    # 사규 CRUD
    path("", views.RegulationListView.as_view(), name="list"),
    path(
        "category/<str:category>/",
        views.CategoryRegulationListView.as_view(),
        name="category_list",
    ),
    path("create/", views.RegulationCreateView.as_view(), name="create"),
    path("<int:pk>/", views.RegulationDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.RegulationUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.RegulationDeleteView.as_view(), name="delete"),
    # 버전 관리
    path(
        "<int:regulation_pk>/version/create/",
        views.RegulationVersionCreateView.as_view(),
        name="version_create",
    ),
    path("<int:pk>/history/", views.regulation_history, name="history"),
    # 파일 다운로드
    path(
        "version/<int:version_pk>/download/",
        views.download_regulation_file,
        name="download",
    ),
    # 태그
    path("tags/", views.tag_list, name="tag_list"),
    path("tags/<str:tag_name>/", views.regulations_by_tag, name="by_tag"),
    # 공통코드 관리
    path("codes/", views.code_list, name="code_list"),
    path("codes/create/", views.code_create, name="code_create"),
    path("codes/<int:pk>/edit/", views.code_update, name="code_update"),
    path("codes/<int:pk>/delete/", views.code_delete, name="code_delete"),
    # API
    path("api/by-category/", views.get_regulations_by_category, name="api_by_category"),
]
