# nCompliance

<p align="center">
  <strong>Corporate Regulation Management System</strong><br>
  사규관리 시스템
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Django-6.0-green.svg" alt="Django">
  <img src="https://img.shields.io/badge/Bootstrap-5.3-purple.svg" alt="Bootstrap">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

---

## 📖 개요

**nCompliance**는 기업의 사규(정책, 규정, 지침, 매뉴얼 등)를 체계적으로 관리하고, 제·개정·폐지 절차를 표준화하는 웹 기반 시스템입니다.

### 주요 특징

- 🔐 **역할 기반 접근 제어** - 4단계 권한 체계 (일반 → 담당자 → 준법지원인 → 관리자)
- 📂 **트리 구조 브라우저** - 그룹/분류/사규 계층 구조로 직관적인 탐색
- 📝 **버전 관리** - 제정/개정/폐지 이력 추적 및 첨부파일 관리
- 🔔 **알림 시스템** - 제개정, 만료예정, 검토요청 알림
- 📊 **보고서** - 제개정 이력, 만료예정 보고서 (Excel 내보내기)

---

## 🚀 빠른 시작

### 요구사항

- Python 3.11+
- pip

### 설치

```bash
# 저장소 클론
git clone https://github.com/daegongs/ncompliance.git
cd ncompliance

# 가상환경 생성 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
python manage.py migrate

# 관리자 계정 생성
python manage.py createsuperuser

# 초기 데이터 생성 (선택)
python manage.py init_companies

# 서버 실행
python manage.py runserver 8080
```

### 접속

- **웹 애플리케이션**: http://localhost:8080/
- **관리자 페이지**: http://localhost:8080/admin/

---

## 🔐 사용자 권한 체계

| 권한 | 역할 코드 | 설명 |
|------|----------|------|
| **일반 사용자** | `GENERAL` | 공개된 사규 조회만 가능 |
| **책임부서 담당자** | `DEPT_MANAGER` | 소관 사규 등록/수정, 본인 부서 데이터만 접근 |
| **준법지원인** | `COMPLIANCE` | 전체 사규 관리, 비공개 사규 조회 |
| **시스템 관리자** | `ADMIN` | 모든 기능, 코드 관리, 사용자 관리, 알림 발송 |

### 권한별 메뉴 접근

| 메뉴 | 일반 | 담당자 | 준법지원인 | 관리자 |
|------|:----:|:------:|:----------:|:------:|
| Home (사규 브라우저) | ✓ | ✓ | ✓ | ✓ |
| 사규 목록/등록 | - | ✓ | ✓ | ✓ |
| 태그 관리 | - | ✓ | ✓ | ✓ |
| 제개정 이력 | - | ✓ | ✓ | ✓ |
| 만료예정 | - | ✓ | ✓ | ✓ |
| 코드 관리 | - | - | - | ✓ |
| 알림 발송 | - | - | - | ✓ |

---

## 📋 주요 기능

### 사규 관리
- **CRUD**: 사규 등록, 조회, 수정, 삭제
- **분류 체계**: 정책/방침, 규정, 지침, 매뉴얼/가이드라인
- **그룹 분류**: 이사회, HR, 재무, 구매, 준법, 반부패, 정보보호, 개인정보보호, 안전보건, ESG
- **상태 관리**: 시행중, 폐지
- **태그 기반 분류** 및 검색
- **상위/하위/관련 사규** 연결

### 사규 브라우저 (Home)
- **트리 구조**: 그룹 → 카테고리 → 사규 계층 표시
- **즐겨찾기**: 자주 보는 사규 즐겨찾기 등록
- **실시간 열람**: 사규 클릭 시 오른쪽 패널에 본문 표시
- **권한별 필터링**: 비공개 사규는 권한자만 표시

### 버전 관리
- 제정/개정/폐지 **이력 추적**
- 버전별 **첨부파일 관리** (PDF, Word, HWP)
- 변경 사유 및 요약 기록

### 접근 권한 관리
- **전체 직원**: 모든 임직원 접근 가능
- **지정된 부서**: 특정 부서 소속 직원만 접근
- **지정된 직원**: 개별 지정된 직원만 접근

### 알림 기능
- 제개정 알림
- 만료예정 알림
- 검토요청 알림
- 시스템 알림 (관리자 발송)

### 보고서
- 제개정 이력 보고서 (Excel 다운로드)
- 만료예정 보고서 (Excel 다운로드)

---

## 🗂 프로젝트 구조

```
ncompliance/
├── accounts/           # 사용자/부서/법인 관리
├── config/             # Django 설정
├── dashboard/          # Home 화면 (사규 브라우저)
├── docs/               # 문서 (요구사항 정의서)
├── notifications/      # 알림 관리
├── regulations/        # 사규 관리 (핵심)
├── reports/            # 보고서
├── templates/          # HTML 템플릿
├── static/             # 정적 파일
├── media/              # 업로드 파일
├── manage.py
├── requirements.txt
└── README.md
```

---

## 📊 기술 스택

| 구분 | 기술 |
|------|------|
| **Backend** | Python 3.13, Django 6.0 |
| **Database** | SQLite (개발), PostgreSQL (운영 권장) |
| **Frontend** | Bootstrap 5, Bootstrap Icons |
| **기타** | openpyxl (Excel), python-docx (Word) |

---

## 📚 문서

- [시스템 개발 요구사항 정의서](docs/System_Requirement_Specification.md)
- [ERD (Entity Relationship Diagram)](ERD.md)

---

## 🧪 테스트 계정

개발/테스트용 계정 (공통 비밀번호: `123!`)

| 아이디 | 역할 | 이름 | 부서 |
|--------|------|------|------|
| `admin` | 시스템관리자 (ADMIN) | 시스템 관리자 | 법무팀 |
| `compliance` | 준법지원인 (COMPLIANCE) | 준법 지원 | 법무팀 |
| `hr_manager` | 책임부서담당 (DEPT_MANAGER) | 인사 담당자 | 인사팀 |
| `fin_manager` | 책임부서담당 (DEPT_MANAGER) | 재무 담당자 | 재무팀 |
| `it_manager` | 책임부서담당 (DEPT_MANAGER) | IT 담당자 | IT팀 |
| `user` | 일반사용자 (GENERAL) | 홍길동 사원 | 사업팀 |

---

## 🤝 기여

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 📞 문의

- **GitHub Issues**: [https://github.com/daegongs/ncompliance/issues](https://github.com/daegongs/ncompliance/issues)

---

<p align="center">
  <sub>© 2024-2026 nCompliance - Corporate Regulation Management System</sub>
</p>
