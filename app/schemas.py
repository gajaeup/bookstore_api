from pydantic import BaseModel, EmailStr
from typing import Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

# 공통 응답 포맷 (API 명세서 준수)
class APIResponse(BaseModel, Generic[T]):
    isSuccess: bool
    message: str
    payload: Optional[T] = None

# 회원가입 요청 DTO
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str

# 로그인 요청 DTO
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 로그인 성공 시 Payload
class Token(BaseModel):
    accessToken: str
    refreshToken: str
    user: dict


# 저자/카테고리 정보 (응답용)
class AuthorResponse(BaseModel):
    author_id: int
    name: str

class CategoryResponse(BaseModel):
    category_id: int
    name: str

# 도서 등록 요청 (관리자용)
class BookCreate(BaseModel):
    title: str
    author: str          # 메인 저자명 (문자열)
    publisher: str
    summary: Optional[str] = None
    price: float
    # 실제 구현에선 저자/카테고리 ID 리스트를 받아서 연결해야 하지만, 
    # 일단 필수 기능 위주로 문자열 데이터부터 처리합니다.

# 도서 정보 응답 (공통)
class BookDto(BaseModel):
    book_id: int
    title: str
    author: str
    publisher: str
    summary: Optional[str] = None
    price: float
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True # ORM 객체를 Pydantic으로 변환 허용

# 페이지네이션 정보
class Pagination(BaseModel):
    totalCount: int
    page: int
    size: int
    totalPages: int

# 도서 목록 응답 (페이지네이션 포함)
class BookListResponse(BaseModel):
    content: list[BookDto]
    pagination: Pagination


# 리뷰 작성 요청
class ReviewCreate(BaseModel):
    rating: int
    content: str

# 리뷰 조회 응답
class ReviewDto(BaseModel):
    review_id: int
    user_id: int
    username: str   # 리뷰 쓴 사람 이름도 보여줘야 함
    rating: int
    content: str
    created_at: Optional[str] = None # 날짜 문자열

    class Config:
        from_attributes = True

# 리뷰 목록 응답
class ReviewListResponse(BaseModel):
    content: list[ReviewDto]
    totalCount: int    

class CartItemCreate(BaseModel):
    book_id: int
    quantity: int = 1

# [리뷰] 수정 요청
class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    content: Optional[str] = None

# 장바구니 수정 요청
class CartItemUpdate(BaseModel):
    quantity: int

# 장바구니 아이템 응답
class CartItemDto(BaseModel):
    cart_item_id: int
    book_id: int
    book_title: str  # 책 제목도 보여주면 좋음
    quantity: int
    price: float     # 가격 정보

    class Config:
        from_attributes = True

# 장바구니 목록 응답
class CartListResponse(BaseModel):
    cart_id: int
    items: list[CartItemDto]
    total_price: float
# --- app/schemas.py (맨 아래에 추가) ---

# 주문 요청에 들어갈 개별 상품
class OrderItemCreate(BaseModel):
    book_id: int
    quantity: int

# 주문 생성 요청 (이걸 받습니다)
class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

# 주문 응답용 DTO
class OrderItemDto(BaseModel):
    book_id: int
    book_title: str
    quantity: int
    price: float

class OrderDto(BaseModel):
    order_id: int
    total_amount: float
    status: str
    created_at: Optional[str] = None
    items: list[OrderItemDto] = []  # 주문에 포함된 책들

    class Config:
        from_attributes = True


# [주문] 상태 변경 요청 (관리자용)
class OrderUpdate(BaseModel):
    status: str  # PENDING, PAID, SHIPPED, CANCELLED

# [위시리스트] 요청 및 응답
class WishlistCreate(BaseModel):
    book_id: int

class WishlistDto(BaseModel):
    wishlist_id: int
    book_id: int
    book_title: str
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True