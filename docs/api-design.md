# 📋 API 설계서 (API Design)

## 1. 개요

본 문서는 온라인 서점 애플리케이션의 RESTful API 명세를 기술합니다.
회원, 도서, 주문, 리뷰 등 핵심 커머스 기능을 모두 포함하며 **JWT 인증**과 **통계 기능**이 적용되었습니다.

## 2. API 엔드포인트 목록

### 🔐 인증 (Auth) - `auth.py`

| Method | URI                 | 설명                               |
| ------ | ------------------- | ---------------------------------- |
| POST   | `/api/signup`       | 회원가입                           |
| POST   | `/api/auth/login`   | 로그인 (Access/Refresh Token 발급) |
| POST   | `/api/auth/logout`  | 로그아웃                           |
| POST   | `/api/auth/refresh` | 토큰 갱신                          |

### 👤 사용자 (Users) - `users.py`

| Method | URI                      | 설명           |
| ------ | ------------------------ | -------------- |
| GET    | `/api/users/me`          | 내 정보 조회   |
| PATCH  | `/api/users/me`          | 회원 정보 수정 |
| DELETE | `/api/users/soft-delete` | 회원 탈퇴      |

### 📚 도서 (Books) - `books.py`

| Method | URI                           | 설명                              |
| ------ | ----------------------------- | --------------------------------- |
| GET    | `/api/public/books`           | 도서 목록 조회 (검색/정렬/페이징) |
| GET    | `/api/public/books/{book_id}` | 도서 상세 조회                    |
| POST   | `/api/admin/books`            | 도서 등록 (관리자)                |
| PATCH  | `/api/admin/books/{book_id}`  | 도서 수정 (관리자)                |
| DELETE | `/api/admin/books/{book_id}`  | 도서 삭제 (관리자)                |

### ⭐ 리뷰 & 좋아요 (Reviews & Likes) - `reviews.py`, `likes.py`

| Method | URI                             | 설명                  |
| ------ | ------------------------------- | --------------------- |
| POST   | `/api/books/{book_id}/reviews`  | 리뷰 작성             |
| GET    | `/api/books/{book_id}/reviews`  | 도서별 리뷰 목록 조회 |
| PATCH  | `/api/reviews/{review_id}`      | 리뷰 수정             |
| DELETE | `/api/reviews/{review_id}`      | 리뷰 삭제             |
| POST   | `/api/reviews/{review_id}/like` | 리뷰 좋아요 등록      |
| DELETE | `/api/reviews/{review_id}/like` | 리뷰 좋아요 취소      |

### 🛒 장바구니 (Carts) - `carts.py`

| Method | URI                          | 설명                 |
| ------ | ---------------------------- | -------------------- |
| POST   | `/api/carts/items`           | 장바구니에 상품 담기 |
| GET    | `/api/carts/items`           | 장바구니 목록 조회   |
| PATCH  | `/api/carts/items/{item_id}` | 수량 변경            |
| DELETE | `/api/carts/items/{item_id}` | 장바구니 상품 삭제   |

### 📦 주문 (Orders) - `orders.py`

| Method | URI                      | 설명                     |
| ------ | ------------------------ | ------------------------ |
| POST   | `/api/orders`            | 주문 생성 (결제)         |
| GET    | `/api/orders`            | 내 주문 내역 조회        |
| PATCH  | `/api/orders/{order_id}` | 주문 상태 변경 (취소 등) |

### 💖 위시리스트 (Wishlists) - `wishlists.py`

| Method | URI                   | 설명            |
| ------ | --------------------- | --------------- |
| POST   | `/api/favorites`      | 위시리스트 추가 |
| GET    | `/api/favorites`      | 위시리스트 조회 |
| DELETE | `/api/favorites/{id}` | 위시리스트 삭제 |

### 📊 통계 (Stats) - `stats.py`

| Method | URI                      | 설명                      |
| ------ | ------------------------ | ------------------------- |
| GET    | `/api/admin/stats/daily` | 일별 매출 통계 (관리자)   |
| GET    | `/api/admin/stats/books` | 도서별 판매 통계 (관리자) |
