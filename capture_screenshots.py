"""
nCompliance 주요 화면 캡처 스크립트
Playwright를 사용하여 각 메뉴 화면을 캡처합니다.
"""

import os
from playwright.sync_api import sync_playwright

# 캡처할 화면 목록
SCREENS = [
    {"name": "01_login", "url": "/accounts/login/", "login_required": False, "desc": "로그인 페이지"},
    {"name": "02_home", "url": "/", "login_required": True, "desc": "Home (사규 브라우저)"},
    {"name": "03_regulation_list", "url": "/regulations/", "login_required": True, "desc": "사규 목록"},
    {"name": "04_regulation_create", "url": "/regulations/create/", "login_required": True, "desc": "사규 등록"},
    {"name": "05_tag_list", "url": "/regulations/tags/", "login_required": True, "desc": "태그 관리"},
    {"name": "06_change_history", "url": "/reports/history/", "login_required": True, "desc": "제개정 이력"},
    {"name": "07_expiry_report", "url": "/reports/expiry/", "login_required": True, "desc": "만료예정"},
    {"name": "08_notification_list", "url": "/notifications/", "login_required": True, "desc": "알림 목록"},
    {"name": "09_notification_create", "url": "/notifications/create/", "login_required": True, "desc": "알림 발송"},
    {"name": "10_code_list", "url": "/regulations/codes/", "login_required": True, "desc": "코드 관리"},
]

BASE_URL = "http://localhost:8080"
OUTPUT_DIR = "docs/screenshots"

# 테스트 계정
USERNAME = "admin"
PASSWORD = "123!"


def main():
    # 출력 디렉토리 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with sync_playwright() as p:
        # 브라우저 실행 (headless 모드)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="ko-KR"
        )
        page = context.new_page()
        
        logged_in = False
        
        for screen in SCREENS:
            print(f"캡처 중: {screen['desc']} ({screen['name']})")
            
            # 로그인이 필요하고 아직 로그인하지 않은 경우
            if screen["login_required"] and not logged_in:
                print("  - 로그인 중...")
                page.goto(f"{BASE_URL}/accounts/login/")
                page.wait_for_load_state("networkidle")
                
                # 로그인 폼 입력
                page.fill('input[name="username"]', USERNAME)
                page.fill('input[name="password"]', PASSWORD)
                page.click('button[type="submit"]')
                page.wait_for_load_state("networkidle")
                logged_in = True
                print("  - 로그인 완료!")
            
            # 페이지 이동
            page.goto(f"{BASE_URL}{screen['url']}")
            page.wait_for_load_state("networkidle")
            
            # 잠시 대기 (렌더링 완료를 위해)
            page.wait_for_timeout(1000)
            
            # 스크린샷 저장
            filepath = os.path.join(OUTPUT_DIR, f"{screen['name']}.png")
            page.screenshot(path=filepath, full_page=False)
            print(f"  -> 저장됨: {filepath}")
        
        # Home 화면에서 사규 선택 후 캡처
        print("캡처 중: Home - 사규 선택 상태")
        page.goto(f"{BASE_URL}/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)
        
        # 트리에서 첫 번째 사규 클릭
        try:
            first_reg = page.locator(".regulation-item").first
            if first_reg.is_visible():
                first_reg.click()
                page.wait_for_timeout(1500)
                filepath = os.path.join(OUTPUT_DIR, "02_home_with_content.png")
                page.screenshot(path=filepath, full_page=False)
                print(f"  -> 저장됨: {filepath}")
        except Exception as e:
            print(f"  (사규 선택 캡처 스킵: {e})")
        
        # 사규 상세 페이지 캡처
        print("캡처 중: 사규 상세")
        page.goto(f"{BASE_URL}/regulations/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)
        
        try:
            # 첫 번째 사규 상세 페이지로 이동
            first_link = page.locator("table tbody tr a").first
            if first_link.is_visible():
                first_link.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(500)
                filepath = os.path.join(OUTPUT_DIR, "04_regulation_detail.png")
                page.screenshot(path=filepath, full_page=False)
                print(f"  -> 저장됨: {filepath}")
        except Exception as e:
            print(f"  (사규 상세 캡처 스킵: {e})")
        
        browser.close()
        
    print("\n" + "="*50)
    print("화면 캡처 완료!")
    print(f"저장 위치: {OUTPUT_DIR}/")
    print("="*50)


if __name__ == "__main__":
    main()
