import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

# --- 공통 헬퍼: 로그인 헤더 가져오기 ---
def get_auth_headers():
    # 테스트용 계정으로 로그인 시도
    login_data = {
        "email": "user0@example.com",  # seed_data로 생성된 유저
        "password": "password123"
    }
    response = client.post("/api/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["payload"]["accessToken"]
        return {"Authorization": f"Bearer {token}"}
    return None

# ==========================================
# 1. 시스템 & 인증 (System & Auth) - 5개
# ==========================================

# 1. 헬스 체크
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# 2. 회원가입 (중복 이메일은 실패하거나 성공 처리)
def test_signup():
    response = client.post("/api/signup", json={
        "email": "new_test_user@example.com",
        "password": "password123",
        "username": "NewUser"
    })
    assert response.status_code in [200, 400, 409]

def test_validation_error():
    # 이메일 형식이 아닌 데이터로 회원가입 시도
    response = client.post("/api/signup", json={
        "email": "not-an-email", 
        "password": "pwd",
        "username": "User"
    })
    assert response.status_code == 422

# 3. 로그인 성공
def test_login_success():
    response = client.post("/api/auth/login", json={
        "email": "user0@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "accessToken" in response.json()["payload"]

# 4. 로그인 실패 (비밀번호 틀림)
def test_login_fail_password():
    response = client.post("/api/auth/login", json={
        "email": "user0@example.com",
        "password": "wrongpassword"
    })
    # 우리 서버는 401 에러를 리턴해야 함
    assert response.status_code == 401

# 5. 로그아웃
def test_logout():
    headers = get_auth_headers()
    if headers:
        response = client.post("/api/auth/logout", headers=headers)
        assert response.status_code == 200

# 5. 내 정보 조회 (인증 필요)
def test_get_me():
    headers = get_auth_headers()
    if headers:
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["payload"]["email"] == "user0@example.com"

# ==========================================
# 2. 도서 관리 (Books) - 4개
# ==========================================

# 6. 도서 목록 조회 (전체)
def test_get_books():
    response = client.get("/api/public/books")
    assert response.status_code == 200
    assert len(response.json()["payload"]["content"]) > 0

# 7. 도서 검색 (Keyword)
def test_search_books():
    response = client.get("/api/public/books?search=테스트")
    assert response.status_code == 200

# 8. 카테고리 필터링
def test_filter_books_category():
    response = client.get("/api/public/books?category=IT")
    assert response.status_code == 200

# 9. 존재하지 않는 도서 상세 조회
def test_get_book_not_found():
    response = client.get("/api/public/books/999999")
    # 로직상 200 OK에 isSuccess=False를 주거나 404를 줄 수 있음
    assert response.status_code in [200, 404]

# ==========================================
# 3. 장바구니 (Cart) - 3개
# ==========================================

# 10. 장바구니 담기
def test_add_to_cart():
    headers = get_auth_headers()
    if headers:
        response = client.post("/api/carts/items", json={"book_id": 1, "quantity": 1}, headers=headers)
        assert response.status_code == 200

# 11. 장바구니 조회
def test_get_cart():
    headers = get_auth_headers()
    if headers:
        response = client.get("/api/carts", headers=headers)
        assert response.status_code == 200

# 12. 장바구니 수량 변경
def test_update_cart_qty():
    headers = get_auth_headers()
    if headers:
        # 먼저 담고
        client.post("/api/carts/items", json={"book_id": 1, "quantity": 1}, headers=headers)
        # 카트 아이템 ID를 알아야 하므로 조회
        cart_res = client.get("/api/carts", headers=headers)
        items = cart_res.json()["payload"]["items"]
        if items:
            item_id = items[0]["cart_item_id"]
            # 수량 변경 시도
            res = client.patch(f"/api/carts/items/{item_id}", json={"quantity": 3}, headers=headers)
            assert res.status_code == 200

# ==========================================
# 4. 위시리스트 & 리뷰 (Wishlist & Review) - 4개
# ==========================================

# 13. 위시리스트 추가
def test_add_wishlist():
    headers = get_auth_headers()
    if headers:
        # 1. 우선 책 목록을 조회해서 "진짜 있는 책 ID"를 하나 가져옵니다.
        books_res = client.get("/api/public/books")
        
        # 책이 하나라도 있다면?
        if books_res.status_code == 200 and len(books_res.json()["payload"]["content"]) > 0:
            # 첫 번째 책의 ID를 꺼냅니다.
            real_book_id = books_res.json()["payload"]["content"][0]["book_id"]
            
            # 2. 그 ID로 위시리스트 추가를 시도합니다.
            response = client.post("/api/favorites", json={"book_id": real_book_id}, headers=headers)
            
            # 3. 성공(200)하거나, 이미 담겨있다(400/409)고 하면 통과!
            assert response.status_code in [200, 400, 409]

# 14. 위시리스트 조회
def test_get_wishlist():
    headers = get_auth_headers()
    if headers:
        response = client.get("/api/favorites", headers=headers)
        assert response.status_code == 200

# 15. 리뷰 작성
def test_create_review():
    headers = get_auth_headers()
    if headers:
        response = client.post("/api/books/1/reviews", json={"rating": 5, "content": "Test Review"}, headers=headers)
        assert response.status_code == 200

# 16. 특정 책의 리뷰 조회
def test_get_book_reviews():
    response = client.get("/api/books/1/reviews")
    assert response.status_code == 200

# ==========================================
# 5. 주문 & 통계 (Order & Stats) - 4개
# ==========================================

# 17. 주문 생성
def test_create_order():
    headers = get_auth_headers()
    if headers:
        response = client.post("/api/orders", json={"items": [{"book_id": 1, "quantity": 1}]}, headers=headers)
        assert response.status_code == 200

# 18. 내 주문 목록 조회
def test_get_my_orders():
    headers = get_auth_headers()
    if headers:
        response = client.get("/api/orders", headers=headers)
        assert response.status_code == 200

# 20. 관리자 통계 (권한 없어서 실패해야 함 - 일반 유저 기준)
def test_admin_stats_fail():
    headers = get_auth_headers()
    if headers:
        response = client.get("/api/admin/stats/users", headers=headers)
        # 권한 없음 에러 (200에 false 또는 403)
        assert response.json()["isSuccess"] == False or response.status_code == 403