# 📚 Online Bookstore Backend API

## 1. 프로젝트 개요
본 프로젝트는 온라인 서점 서비스를 위한 백엔드 API 서버입니다.
사용자 관리, 도서 검색 및 조회, 장바구니, 주문 결제, 리뷰 및 커뮤니티 기능, 그리고 관리자 통계 기능을 제공합니다.

### 🎯 주요 기능
- **사용자(User):** 회원가입, 로그인(JWT), 내 정보 관리, 회원 탈퇴
- **도서(Book):** 도서 목록 조회(검색/정렬/페이징), 상세 조회
- **리뷰(Review):** 도서 리뷰 및 평점 작성, 댓글(대댓글) 기능, 좋아요
- **커머스(Commerce):** 장바구니 담기, 주문 생성, 주문 내역 조회
- **편의기능:** 위시리스트(찜하기), 통계(관리자용 일별/상품별 매출)

---

## 2. 실행 방법

### 로컬 실행 (Local Development)
Python 3.12 환경에서 아래 명령어를 순서대로 실행하세요.

```bash
# 1. 저장소 복제 및 이동
git clone [https://github.com/gajaeup/bookstore.git](https://github.com/gajaeup/bookstore.git)
cd bookstore

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)

# 3. 의존성 패키지 설치
pip install -r requirements.txt

# 4. 데이터베이스 초기화 (마이그레이션 및 시드 데이터)
# (.env 파일이 설정되어 있어야 합니다)
python seed_data.py

# 5. 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
---

## 3. 환경 변수


---


## 4. 배포주소(JCloud)
Base URL: http://113.198.66.75:10049

Swagger UI (API 문서): http://113.198.66.75:10049/docs

Health Check: http://113.198.66.75:10049/health



---


## 5. 인증 플로우 및 역할(Role)
인증 방식 (JWT)
로그인: POST /api/auth/login 요청 시 Access Token 및 Refresh Token 발급

API 요청: HTTP Header에 Authorization: Bearer <Access Token> 포함하여 요청

토큰 갱신: Access Token 만료 시 POST /api/auth/refresh로 갱신


|역할 (Role)|권한 범위|접근 가능 API 예시|
|---|---|---|
|ROLE_USER|일반 사용자|도서 조회, 리뷰 작성, 장바구니, 주문|
|ROLE_ADMIN|관리자|도서 등록/수정/삭제, 매출 통계 조회|



## 6. 예제 계정 (Test Accounts)
seed_data.py 실행 시 자동으로 생성되는 테스트 계정입니다.

|역할|이메일 (ID)|비밀번호|비고|
|---|---|---|---|
|관리자|admin@example.com|password123|모든 관리자 기능 접근 가능|
|일반 유저|user1@example.com|password123|일반적인 쇼핑몰 기능 테스트용|
|일반 유저|user2@example.com|password123|리뷰/댓글 상호작용 테스트용|

---

## 7. DB 연결 정보 (테스트용)
JCloud 서버 내부 또는 로컬 테스트 시 사용되는 DB 정보입니다.

Database: MySQL 8.0

Host: localhost (서버 내부 기준)

Port: 3306

DB Name: bookstore

User: root

Password: (별도 제출된 텍스트 파일 확인)

---


## 8.엔드포인트 요약표

|카테고리|Method|URL|설명|
|---|---|---|---|
|Auth|POST|/api/auth/login|로그인|
|Users|GET|/api/users/me|내 정보 조회|
|Books|GET|/api/public/books|도서 목록 (페이징/검색)|
|Reviews|POST|/api/books/{id}/reviews|리뷰 작성|
|Carts|POST|/api/carts/items|장바구니 담기|
|Orders|POST|/api/orders|주문 생성|
|Stats|GET|/api/admin/stats/daily|일별 매출 통계 (관리자)|


---

## 9. 성능/보안 고려사항
보안 (Security)
비밀번호 암호화: bcrypt 해싱 알고리즘을 사용하여 DB에 안전하게 저장.

CORS 설정: 프론트엔드와의 연동을 고려하여 CORSMiddleware 적용.

Rate Limiting: slowapi를 사용하여 과도한 요청 방지 (DDoS 방어 기초).

성능 (Performance)
Pagination: 도서 및 리뷰 목록 조회 시 page, size를 통한 페이징 처리로 DB 부하 감소.

Indexing: email, book_id 등 자주 조회되는 컬럼에 DB 인덱스 적용 (MySQL).

FK 관계 최적화: SQLAlchemy relationship을 효율적으로 설정하여 N+1 문제 최소화.

---


## 10. 한계와 개선 계획
비동기 DB 처리: 현재 pymysql(동기) 드라이버를 사용 중이나, 향후 aiomysql로 전환하여 async/await 성능을 극대화할 계획입니다.

캐싱 도입: 베스트셀러나 인기 리뷰 조회 성능 향상을 위해 Redis 캐싱 도입을 고려 중입니다.
