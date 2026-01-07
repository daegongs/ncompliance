# nCompliance - 사규관리 시스템
**Corporate Regulation Management System**

회사의 사규를 체계적으로 관리하고, 제·개정·폐지 절차를 표준화하는 웹 기반 시스템입니다.

---

## 🔐 사용자 권한 체계

### 권한별 역할 및 접근 범위

| 권한 | 역할 코드 | 설명 | 접근 범위 |
|------|----------|------|----------|
| **일반 사용자** | `GENERAL` | 일반 임직원 | 사규 조회 (공개 사규만) |
| **사규관리 담당자** | `DEPT_MANAGER` | 책임부서 담당자 | 소관 사규 등록/수정, 사규 관리 메뉴 |
| **준법지원인** | `COMPLIANCE` | 준법지원인 | 전체 사규 관리, 비공개 사규 조회 |
| **시스템 관리자** | `ADMIN` | 시스템 관리자 | 모든 기능, 코드 관리, 시스템 설정 |

### 권한별 메뉴 접근

| 메뉴 | 일반 사용자 | 사규관리 담당자 | 준법지원인 | 시스템 관리자 |
|------|:-----------:|:--------------:|:----------:|:-------------:|
| Home (사규 브라우저) | ✓ | ✓ | ✓ | ✓ |
| 사규 목록 | - | ✓ | ✓ | ✓ |
| 사규 등록 | - | ✓ | ✓ | ✓ |
| 태그 관리 | - | ✓ | ✓ | ✓ |
| 제개정 이력 | - | ✓ | ✓ | ✓ |
| 만료예정 | - | ✓ | ✓ | ✓ |
| 코드 관리 | - | - | - | ✓ |
| 알림 발송 | - | - | - | ✓ |
| Django 관리자 | - | - | - | ✓ |
| 알림 | ✓ | ✓ | ✓ | ✓ |
| 내 정보 | ✓ | ✓ | ✓ | ✓ |

---

## 📋 주요 기능

### 1. 사규 관리
- **사규 CRUD**: 등록, 조회, 수정, 삭제
- **분류 체계**: 정책/방침, 규정, 지침, 매뉴얼/가이드라인
- **그룹 분류**: 이사회, HR, 재무, 구매, 준법, 반부패, 정보보호, 개인정보보호, 안전보건, ESG
- **상태 관리**: 시행중, 폐지
- **태그 기반 분류** 및 검색
- **상위/하위/관련 사규** 연결

### 2. Home 화면 (사규 브라우저)
- **트리 구조**: 그룹 → 카테고리 → 사규 계층 표시
- **즐겨찾기**: 자주 보는 사규 즐겨찾기 등록
- **실시간 열람**: 사규 클릭 시 오른쪽 패널에 본문 표시
- **권한별 필터링**: 비공개 사규는 권한자만 표시

### 3. 버전 관리
- 사규 제정/개정/폐지 **이력 추적**
- 버전별 **첨부파일 관리**
- 변경 사유 및 요약 기록

### 4. 접근 권한 관리
- **전체 직원**: 모든 임직원 접근 가능
- **지정된 부서**: 특정 부서 소속 직원만 접근
- **지정된 직원**: 개별 지정된 직원만 접근
- **임직원 공개 여부**: 비공개 사규 관리

### 5. 공통코드 관리 (시스템 관리자 전용)
- **그룹 코드**: 사규 그룹 분류
- **분류 코드**: 사규 카테고리
- **상태 코드**: 시행 상태
- **변경유형 코드**: 제정/개정/폐지

### 6. 알림 기능
- **제개정 알림**: 사규 변경 시 알림
- **만료예정 알림**: 정기검토 예정 알림
- **검토요청 알림**: 담당자 요청 알림
- **시스템 알림**: 관리자 발송 알림

### 7. 보고서
- **제개정 이력**: 사규 변경 이력 조회
- **만료예정**: 정기검토 예정 사규 목록

---

## 🗂 프로젝트 구조

```
ncompliance/
├── accounts/           # 사용자/부서/법인 관리
├── config/             # Django 설정
├── dashboard/          # Home 화면 (사규 브라우저)
├── notifications/      # 알림 관리
├── regulations/        # 사규 관리 (핵심)
├── reports/            # 보고서
├── templates/          # HTML 템플릿
├── static/             # 정적 파일
├── media/              # 업로드 파일
├── reference/          # 참조 데이터
├── manage.py
├── requirements.txt
└── db.sqlite3
```

---

## ⚙️ 설치 및 실행

### 1. 의존성 설치

```powershell
py -m pip install -r requirements.txt
```

### 2. 데이터베이스 마이그레이션

```powershell
py manage.py migrate
```

### 3. 초기 데이터 생성 (선택)

```powershell
# 법인/부서 초기화
py manage.py init_companies

# 사규 데이터 임포트 (Excel)
py manage.py import_naver_regulations --file=./reference/naver_regulation_sample.xlsx
```

### 4. 관리자 계정 생성

```powershell
py manage.py createsuperuser
```

### 5. 서버 실행

```powershell
py manage.py runserver 0.0.0.0:8080
```

### 6. 접속

- **웹 애플리케이션**: http://localhost:8080/
- **Django 관리자**: http://localhost:8080/admin/

---

## 🔧 Django Admin 메뉴

### 사규 관리
- 사규 (Regulation)
- 사규 버전 (RegulationVersion)
- 태그 (RegulationTag)
- 즐겨찾기 (Favorite)
- 공통코드 (CommonCode)
- 다운로드 로그 (RegulationDownloadLog)

### 사용자 관리
- 법인 (Company)
- 부서 (Department)
- 사용자 (User)

---

## 📊 기술 스택

- **Backend**: Django 6.0, Python 3.13
- **Database**: SQLite (개발), PostgreSQL (운영 권장)
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **기타**: openpyxl (Excel 처리)

---

© 2024-2026 nCompliance - Corporate Regulation Management System
