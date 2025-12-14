# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

# --- Enums ---
class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


# --- 1. User & Auth ---
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Relationships
    reviews = relationship("Review", back_populates="user")
    cart = relationship("Cart", uselist=False, back_populates="user")
    orders = relationship("Order", back_populates="user")
    wishlist = relationship("Wishlist", back_populates="user")

# --- 2. Book & Meta ---
class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False) # 메인 저자명 (단순 표시용)
    publisher = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    # [수정] categories 관계 삭제됨
    authors = relationship("Author", secondary="book_authors", back_populates="books")
    reviews = relationship("Review", back_populates="book")

class Author(Base):
    __tablename__ = "authors"
    author_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    books = relationship("Book", secondary="book_authors", back_populates="authors")

# [수정] class Category 삭제됨

# Association Tables (N:M)
class BookAuthor(Base):
    __tablename__ = "book_authors"
    book_id = Column(Integer, ForeignKey("books.book_id"), primary_key=True)
    author_id = Column(Integer, ForeignKey("authors.author_id"), primary_key=True)

# [수정] class BookCategory 삭제됨


# --- 3. Review & Interaction ---
class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    rating = Column(Integer, nullable=False) # 1~5
    content = Column(Text, nullable=True)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")

class ReviewLike(Base):
    __tablename__ = "review_likes"
    review_id = Column(Integer, ForeignKey("reviews.review_id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)


# --- 4. Commerce & User Library ---
class Wishlist(Base):
    __tablename__ = "wishlists"
    wishlist_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="wishlist")
    book = relationship("Book")

class Cart(Base):
    __tablename__ = "carts"
    cart_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart")

class CartItem(Base):
    __tablename__ = "cart_items"
    cart_item_id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.cart_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=func.now())

    cart = relationship("Cart", back_populates="items")
    book = relationship("Book")

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    book = relationship("Book")

class TokenBlocklist(Base):
    __tablename__ = "token_blocklist"
    
    token = Column(String(500), primary_key=True)
    created_at = Column(DateTime, default=func.now())