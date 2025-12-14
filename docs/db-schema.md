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

### **4. Carts (장바구니)**

### **Carts**

사용자의 장바구니(바구니 자체)입니다.
| 컬럼명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `cart_id` | INTEGER (PK) | 장바구니 ID |
| `user_id` | INTEGER (FK) | 소유자 ID |
| `created_at` | DATETIME | 생성 일시 |

### **CartItems**

장바구니에 담긴 개별 상품들입니다.
| 컬럼명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `cart_item_id` | INTEGER (PK) | 장바구니 아이템 ID |
| `cart_id` | INTEGER (FK) | 장바구니 ID |
| `book_id` | INTEGER (FK) | 담은 도서 ID |
| `quantity` | INTEGER | 수량 (Default: 1) |

### **Orders**

사용자의 주문 내역입니다.
| 컬럼명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `order_id` | INTEGER (PK) | 주문 고유 ID |
| `user_id` | INTEGER (FK) | 주문자 ID |
| `total_amount` | DECIMAL(10,2) | 총 결제 금액 |
| `status` | ENUM | 상태 ('PENDING', 'PAID', 'SHIPPED', 'CANCELLED') |
| `created_at` | DATETIME | 주문 일시 |

### **OrderItems**

주문 상품의 상세 정보입니다.
| 컬럼명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `order_item_id` | INTEGER (PK) | 주문 상세 ID |
| `order_id` | INTEGER (FK) | 상위 주문 ID |
| `book_id` | INTEGER (FK) | 도서 ID |
| `quantity` | INTEGER | 주문 수량 |
| `price` | DECIMAL(10,2) | 도서 가격|

---

### **5. Wishlist (위시리스트)**

| 컬럼명        | 타입         | 설명          |
| ------------- | ------------ | ------------- |
| `wishlist_id` | INTEGER (PK) | 위시리스트 ID |
| `user_id`     | INTEGER (FK) | 사용자 ID     |
| `book_id`     | INTEGER (FK) | 도서 ID       |
| `created_at`  | DATETIME     | 찜한 날짜     |
