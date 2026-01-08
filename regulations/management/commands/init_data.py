"""
초기 데이터 생성 명령어
샘플 부서, 사용자, 사규 데이터 생성
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, Department
from regulations.models import Regulation, RegulationVersion, RegulationTag


class Command(BaseCommand):
    help = '초기 샘플 데이터 생성'

    def handle(self, *args, **options):
        self.stdout.write('초기 데이터 생성 시작...')
        
        # 1. 부서 생성
        self.stdout.write('  - 부서 생성 중...')
        departments = self.create_departments()
        
        # 2. 사용자 생성
        self.stdout.write('  - 사용자 생성 중...')
        users = self.create_users(departments)
        
        # 3. 태그 생성
        self.stdout.write('  - 태그 생성 중...')
        tags = self.create_tags()
        
        # 4. 사규 생성
        self.stdout.write('  - 사규 생성 중...')
        regulations = self.create_regulations(departments, users, tags)
        
        self.stdout.write(self.style.SUCCESS('초기 데이터 생성 완료!'))
        self.stdout.write(f'  - 부서: {len(departments)}개')
        self.stdout.write(f'  - 사용자: {len(users)}개')
        self.stdout.write(f'  - 태그: {len(tags)}개')
        self.stdout.write(f'  - 사규: {len(regulations)}개')

    def create_departments(self):
        departments = []
        dept_data = [
            {'code': 'EXEC', 'name': '경영진'},
            {'code': 'LEGAL', 'name': '법무/준법지원팀'},
            {'code': 'HR', 'name': '인사팀'},
            {'code': 'FIN', 'name': '재무팀'},
            {'code': 'IT', 'name': 'IT팀'},
            {'code': 'AUDIT', 'name': '감사팀'},
            {'code': 'BIZ', 'name': '사업팀'},
            {'code': 'PURCHASE', 'name': '구매팀'},
        ]
        
        for data in dept_data:
            dept, created = Department.objects.get_or_create(
                code=data['code'],
                defaults={'name': data['name']}
            )
            departments.append(dept)
        
        return departments

    def create_users(self, departments):
        users = []
        
        # 관리자 계정
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@company.com',
                'first_name': '관리자',
                'last_name': '시스템',
                'employee_id': 'EMP001',
                'role': 'ADMIN',
                'department': departments[1],  # 법무팀
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin.set_password('123!')
        admin.save()
        users.append(admin)
        
        # 준법지원인
        compliance, created = User.objects.get_or_create(
            username='compliance',
            defaults={
                'email': 'compliance@company.com',
                'first_name': '지원',
                'last_name': '준법',
                'employee_id': 'EMP002',
                'role': 'COMPLIANCE',
                'department': departments[1],
                'position': '준법지원인',
            }
        )
        compliance.set_password('123!')
        compliance.save()
        users.append(compliance)
        
        # 부서 담당자들
        dept_managers = [
            ('hr_manager', '담당자', '인사', 'EMP003', 'DEPT_MANAGER', departments[2]),
            ('fin_manager', '담당자', '재무', 'EMP004', 'DEPT_MANAGER', departments[3]),
            ('it_manager', '담당자', 'IT', 'EMP005', 'DEPT_MANAGER', departments[4]),
        ]
        
        for username, first, last, emp_id, role, dept in dept_managers:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@company.com',
                    'first_name': first,
                    'last_name': last,
                    'employee_id': emp_id,
                    'role': role,
                    'department': dept,
                }
            )
            user.set_password('123!')
            user.save()
            users.append(user)
        
        # 일반 사용자
        general, created = User.objects.get_or_create(
            username='user',
            defaults={
                'email': 'user@company.com',
                'first_name': '사원',
                'last_name': '홍길동',
                'employee_id': 'EMP010',
                'role': 'GENERAL',
                'department': departments[6],
            }
        )
        general.set_password('123!')
        general.save()
        users.append(general)
        
        return users

    def create_tags(self):
        tags = []
        tag_names = ['인사', '재무', '보안', '윤리', '구매', '개인정보', 'IT', '내부통제', '감사', '준법']
        
        for name in tag_names:
            tag, created = RegulationTag.objects.get_or_create(name=name)
            tags.append(tag)
        
        return tags

    def create_regulations(self, departments, users, tags):
        regulations = []
        today = timezone.now().date()
        
        # 사규 데이터
        reg_data = [
            # 정책/방침
            {
                'code': 'POL-001',
                'title': '인권경영정책',
                'category': 'POLICY',
                'description': '회사의 인권경영에 대한 기본 원칙과 방향을 제시하는 최상위 정책입니다.',
                'responsible_dept': departments[0],  # 경영진
                'tags': ['윤리', '인사'],
            },
            {
                'code': 'POL-002',
                'title': '부패방지 경영방침',
                'category': 'POLICY',
                'description': '부패 및 뇌물 방지에 대한 회사의 기본 입장과 원칙을 선언합니다.',
                'responsible_dept': departments[1],  # 법무팀
                'tags': ['윤리', '준법'],
            },
            {
                'code': 'POL-003',
                'title': '정보보호정책',
                'category': 'POLICY',
                'description': '회사의 정보자산 보호에 관한 기본 원칙입니다.',
                'responsible_dept': departments[4],  # IT팀
                'tags': ['보안', 'IT'],
            },
            # 규정
            {
                'code': 'REG-001',
                'title': '인사관리규정',
                'category': 'REGULATION',
                'description': '임직원의 채용, 평가, 보상 등 인사 전반에 관한 기본 규정입니다.',
                'responsible_dept': departments[2],  # 인사팀
                'tags': ['인사'],
            },
            {
                'code': 'REG-002',
                'title': '구매관리규정',
                'category': 'REGULATION',
                'description': '회사의 구매 업무에 관한 기본 원칙과 절차를 규정합니다.',
                'responsible_dept': departments[7],  # 구매팀
                'tags': ['구매', '내부통제'],
            },
            {
                'code': 'REG-003',
                'title': '준법통제기준',
                'category': 'REGULATION',
                'description': '회사의 준법경영체계 및 준법통제 기준을 규정합니다.',
                'responsible_dept': departments[1],  # 법무팀
                'tags': ['준법', '내부통제'],
            },
            {
                'code': 'REG-004',
                'title': '개인정보처리규정',
                'category': 'REGULATION',
                'description': '개인정보의 수집, 이용, 제공, 파기 등에 관한 규정입니다.',
                'responsible_dept': departments[1],  # 법무팀
                'tags': ['개인정보', '보안'],
            },
            # 지침
            {
                'code': 'GDL-001',
                'title': '부패방지 지침',
                'category': 'GUIDELINE',
                'description': '부패방지 경영방침의 세부 시행 기준 및 절차를 규정합니다.',
                'responsible_dept': departments[1],  # 법무팀
                'tags': ['윤리', '준법'],
                'parent_code': 'POL-002',
            },
            {
                'code': 'GDL-002',
                'title': '징계 심의위원회 운영 기준',
                'category': 'GUIDELINE',
                'description': '징계 심의위원회의 구성 및 운영에 관한 세부 기준입니다.',
                'responsible_dept': departments[2],  # 인사팀
                'tags': ['인사'],
                'parent_code': 'REG-001',
            },
            {
                'code': 'GDL-003',
                'title': '정보시스템 보안지침',
                'category': 'GUIDELINE',
                'description': '정보시스템의 보안 관리에 관한 세부 지침입니다.',
                'responsible_dept': departments[4],  # IT팀
                'tags': ['보안', 'IT'],
                'parent_code': 'POL-003',
            },
            # 매뉴얼/가이드라인
            {
                'code': 'MNL-001',
                'title': '구매기안 가이드라인',
                'category': 'MANUAL',
                'description': '구매 기안 작성 시 참고할 수 있는 가이드라인입니다.',
                'responsible_dept': departments[7],  # 구매팀
                'is_mandatory': False,
                'tags': ['구매'],
            },
        ]
        
        created_regs = {}
        admin_user = users[0]
        
        for data in reg_data:
            parent = None
            if 'parent_code' in data:
                parent = created_regs.get(data['parent_code'])
            
            reg, created = Regulation.objects.get_or_create(
                code=data['code'],
                defaults={
                    'title': data['title'],
                    'category': data['category'],
                    'description': data['description'],
                    'responsible_dept': data['responsible_dept'],
                    'is_mandatory': data.get('is_mandatory', True),
                    'scope': 'ALL' if data['category'] != 'GUIDELINE' else 'DEPT',
                    'status': 'ACTIVE',
                    'current_version': '1.0',
                    'effective_date': today - timedelta(days=180),
                    'expiry_date': today + timedelta(days=180),
                    'parent_regulation': parent,
                    'created_by': admin_user,
                }
            )
            
            created_regs[data['code']] = reg
            
            # 태그 연결
            if 'tags' in data:
                for tag_name in data['tags']:
                    tag = RegulationTag.objects.get(name=tag_name)
                    tag.regulations.add(reg)
            
            # 버전 생성
            if created:
                RegulationVersion.objects.get_or_create(
                    regulation=reg,
                    version_number='1.0',
                    defaults={
                        'change_type': 'CREATE',
                        'change_reason': '최초 제정',
                        'created_by': admin_user,
                    }
                )
            
            regulations.append(reg)
        
        return regulations






