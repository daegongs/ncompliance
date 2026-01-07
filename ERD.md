# nCompliance ERD (Entity Relationship Diagram)

## 모델 관계도

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    accounts 앱                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────┐        ┌─────────────┐        ┌─────────────┐                     │
│  │   Company   │───1:N──│ Department  │───1:N──│    User     │                     │
│  │  (법인)     │        │  (부서)     │        │  (사용자)   │                     │
│  └─────────────┘        └──────┬──────┘        └─────────────┘                     │
│                                │                                                     │
│                           self (상위부서)                                           │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   regulations 앱                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────┐                                                                    │
│  │ CommonCode  │  (공통코드: 그룹, 분류, 상태, 변경유형)                            │
│  └─────────────┘                                                                    │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                            Regulation (사규)                                 │   │
│  │  - code (사규코드, UK)                                                       │   │
│  │  - title (사규명)                                                            │   │
│  │  - category (분류: POLICY/REGULATION/GUIDELINE/MANUAL)                       │   │
│  │  - group (그룹: HR, 재무, 준법 등)                                           │   │
│  │  - status (상태: ACTIVE/ABOLISHED)                                           │   │
│  │  - is_mandatory (의무준수)                                                   │   │
│  │  - is_public (임직원 공개)                                                   │   │
│  │  - responsible_dept (책임부서) → Department                                  │   │
│  │  - manager (사규관리 담당자)                                                 │   │
│  │  - manager_primary (사규관리 책임자)                                         │   │
│  │  - content (규정 본문)                                                       │   │
│  │  - original_file (원본 파일)                                                 │   │
│  │  - reference_url (참조 링크)                                                 │   │
│  │  - access_level (접근권한: ALL/DEPARTMENTS/USERS)                            │   │
│  │  - allowed_companies (M:N) → Company                                         │   │
│  │  - allowed_departments (M:N) → Department                                    │   │
│  │  - allowed_users (M:N) → User                                                │   │
│  │  - parent_regulation (상위사규) → self                                       │   │
│  │  - related_regulations (M:N) → self                                          │   │
│  └────────────────────────────────┬────────────────────────────────────────────┘   │
│                                   │                                                 │
│            ┌──────────────────────┼──────────────────────┐                         │
│            │                      │                      │                         │
│            ▼                      ▼                      ▼                         │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐                  │
│  │ RegulationVersion│   │  RegulationTag  │   │    Favorite     │                  │
│  │   (사규 버전)    │   │    (태그)       │   │   (즐겨찾기)    │                  │
│  │                 │   │                 │   │                 │                  │
│  │ - version_number│   │ - name (태그명) │   │ - user → User   │                  │
│  │ - change_type   │   │ - regulations   │   │ - regulation    │                  │
│  │ - change_reason │   │   (M:N)         │   │ - created_at    │                  │
│  │ - content_file  │   │                 │   │                 │                  │
│  │ - approved_by   │   └─────────────────┘   └─────────────────┘                  │
│  │ - approved_at   │                                                               │
│  └─────────────────┘                                                               │
│                                                                                     │
│  ┌─────────────────────┐                                                           │
│  │ RegulationDownloadLog│  (다운로드 로그)                                         │
│  │ - regulation        │                                                           │
│  │ - version           │                                                           │
│  │ - user              │                                                           │
│  │ - ip_address        │                                                           │
│  │ - downloaded_at     │                                                           │
│  └─────────────────────┘                                                           │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                  notifications 앱                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────┐        ┌─────────────────────────┐                        │
│  │    Notification     │        │  NotificationSetting    │                        │
│  │     (알림)          │        │    (알림 설정)          │                        │
│  │                     │        │                         │                        │
│  │ - user → User       │        │ - user → User (1:1)     │                        │
│  │ - regulation → Reg  │        │ - receive_change        │                        │
│  │ - notification_type │        │ - receive_expiry        │                        │
│  │ - title             │        │ - receive_review        │                        │
│  │ - message           │        │ - email_notification    │                        │
│  │ - is_read           │        │                         │                        │
│  │ - read_at           │        │                         │                        │
│  └─────────────────────┘        └─────────────────────────┘                        │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 주요 관계

### 1. 사용자-부서-법인
- Company 1:N Department (법인 → 부서)
- Department N:1 Company (부서 → 법인)
- Department self-reference (상위부서)
- User N:1 Company (사용자 → 법인)
- User N:1 Department (사용자 → 부서)

### 2. 사규-부서-사용자
- Regulation N:1 Department (사규 → 책임부서)
- Regulation M:N Company (사규 → 허용 법인)
- Regulation M:N Department (사규 → 허용 부서)
- Regulation M:N User (사규 → 허용 사용자)

### 3. 사규-버전
- Regulation 1:N RegulationVersion (사규 → 버전)
- RegulationVersion N:1 User (버전 → 승인자, 작성자)

### 4. 사규-태그
- Regulation M:N RegulationTag (사규 ↔ 태그)

### 5. 사규-즐겨찾기
- Favorite N:1 User (즐겨찾기 → 사용자)
- Favorite N:1 Regulation (즐겨찾기 → 사규)
- User-Regulation unique_together

### 6. 알림
- Notification N:1 User (알림 → 수신자)
- Notification N:1 Regulation (알림 → 관련사규, nullable)
- NotificationSetting 1:1 User (설정 ↔ 사용자)

## User 역할 (ROLE_CHOICES)

| 코드 | 설명 | 권한 |
|------|------|------|
| `GENERAL` | 일반 | 공개 사규 조회 |
| `DEPT_MANAGER` | 책임부서담당 | 소관 사규 관리 |
| `COMPLIANCE` | 준법지원인 | 전체 사규 관리 |
| `ADMIN` | 관리자 | 시스템 전체 관리 |

## CommonCode 유형 (CODE_TYPE_CHOICES)

| 코드 | 설명 | 용도 |
|------|------|------|
| `GROUP` | 그룹 | 사규 그룹 분류 (HR, 재무 등) |
| `CATEGORY` | 분류 | 사규 카테고리 |
| `STATUS` | 상태 | 사규 시행 상태 |
| `CHANGE_TYPE` | 변경유형 | 제정/개정/폐지 |
| `CUSTOM` | 사용자정의 | 확장용 |
