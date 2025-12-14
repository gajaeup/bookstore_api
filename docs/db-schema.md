# 🗄️ 데이터베이스 스키마 (Database Schema)

## 1. 개요

본 프로젝트는 **MySQL 8.0**을 사용하며, 사용자, 상품, 주문, 리뷰 등 전자상거래 서비스를 위한 완전한 관계형 데이터 모델을 갖추고 있습니다.

## 2. 테이블 상세 정의

### **1. Users (사용자)**

| 컬럼명       | 타입         | 설명                   |
| ------------ | ------------ | ---------------------- |
| `user_id`    | INTEGER (PK) | 사용자 고유 ID         |
| `email`      | VARCHAR      | 이메일 (로그인 ID)     |
| `role`       | ENUM         | 권한 ('USER', 'ADMIN') |
| `created_at` | DATETIME     | 가입일                 |

### **2. Books (도서)**

| 컬럼명    | 타입         | 설명      |
| --------- | ------------ | --------- |
| `book_id` | INTEGER (PK) | 도서 ID   |
| `title`   | VARCHAR      | 도서 제목 |
| `author`  | VARCHAR      | 저자명    |
| `price`   | DECIMAL      | 가격      |
| `stock`   | INTEGER      | 재고 수량 |

### **3. Reviews & Likes (리뷰/좋아요)**

| 컬럼명      | 타입         | 설명       |
| ----------- | ------------ | ---------- |
| `review_id` | INTEGER (PK) | 리뷰 ID    |
| `user_id`   | INTEGER (FK) | 작성자 ID  |
| `book_id`   | INTEGER (FK) | 도서 ID    |
| `rating`    | INTEGER      | 평점 (1~5) |
| `content`   | TEXT         | 리뷰 내용  |
| `likes`     | INTEGER      | 좋아요 수  |

### **4. Commerce (주문/장바구니)**

| 테이블         | 설명               | 주요 컬럼                                 |
| -------------- | ------------------ | ----------------------------------------- |
| **Carts**      | 장바구니           | `cart_id`, `user_id`                      |
| **CartItems**  | 장바구니 상세 품목 | `book_id`, `quantity`                     |
| **Orders**     | 주문 정보          | `total_amount`, `status` (PAID/CANCELLED) |
| **OrderItems** | 주문 상세 품목     | `price` (구매 당시 가격), `quantity`      |

### **5. Wishlist (위시리스트)**

| 컬럼명        | 타입         | 설명          |
| ------------- | ------------ | ------------- |
| `wishlist_id` | INTEGER (PK) | 위시리스트 ID |
| `user_id`     | INTEGER (FK) | 사용자 ID     |
| `book_id`     | INTEGER (FK) | 도서 ID       |
