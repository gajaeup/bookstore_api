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

class LibraryStatus(str, enum.Enum):
    READING = "reading"
    READ = "read"

# --- 1. User & Auth ---
class User(Base):
    __tablename__ = "users" # [cite: 34]

    user_id = Column(Integer, primary_key=True, index=True) # [cite: 35]
    email = Column(String(255), unique=True, nullable=False) # [cite: 36]
    password = Column(String(255), nullable=False) # [cite: 37]
    username = Column(String(255), nullable=False) # [cite: 42]
    role = Column(Enum(UserRole), default=UserRole.USER) # [cite: 44, 48]
    created_at = Column(DateTime, default=func.now()) # [cite: 45]
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) # [cite: 46]
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Relationships
    reviews = relationship("Review", back_populates="user")
    cart = relationship("Cart", uselist=False, back_populates="user")
    orders = relationship("Order", back_populates="user")
    library_books = relationship("Library", back_populates="user")
    wishlist = relationship("Wishlist", back_populates="user")

# --- 2. Book & Meta ---
class Book(Base):
    __tablename__ = "books" # [cite: 52]

    book_id = Column(Integer, primary_key=True, index=True) # [cite: 52]
    title = Column(String(255), nullable=False) # [cite: 197]
    author = Column(String(255), nullable=False) # 메인 저자명 (단순 표시용) [cite: 197]
    publisher = Column(String(255), nullable=False) # [cite: 207]
    summary = Column(Text, nullable=True) # [cite: 193]
    price = Column(DECIMAL(10, 2), nullable=False) # [cite: 194]
    created_at = Column(DateTime, default=func.now()) # [cite: 194]
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    authors = relationship("Author", secondary="book_authors", back_populates="books")
    categories = relationship("Category", secondary="book_categories", back_populates="books")
    reviews = relationship("Review", back_populates="book")

class Author(Base):
    __tablename__ = "authors" # [cite: 199]
    author_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    books = relationship("Book", secondary="book_authors", back_populates="authors")

class Category(Base):
    __tablename__ = "categories" # [cite: 233]
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    books = relationship("Book", secondary="book_categories", back_populates="categories")

# Association Tables (N:M)
class BookAuthor(Base):
    __tablename__ = "book_authors" # [cite: 201]
    book_id = Column(Integer, ForeignKey("books.book_id"), primary_key=True)
    author_id = Column(Integer, ForeignKey("authors.author_id"), primary_key=True)

class BookCategory(Base):
    __tablename__ = "book_categories" # [cite: 237]
    book_id = Column(Integer, ForeignKey("books.book_id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), primary_key=True)

# --- 3. Review & Interaction ---
class Review(Base):
    __tablename__ = "reviews" # [cite: 68]

    review_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    rating = Column(Integer, nullable=False) # 1~5 Check logic in code [cite: 224]
    content = Column(Text, nullable=True) # [cite: 230]
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")
    comments = relationship("Comment", back_populates="review")

class ReviewLike(Base):
    __tablename__ = "review_likes" # [cite: 258]
    review_id = Column(Integer, ForeignKey("reviews.review_id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)

class Comment(Base):
    __tablename__ = "comments" # [cite: 215]

    comment_id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.review_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    username = Column(String(255), nullable=False) # 스냅샷용 [cite: 231]
    parent_id = Column(Integer, ForeignKey("comments.comment_id"), nullable=True) # 대댓글 [cite: 243]
    content = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    review = relationship("Review", back_populates="comments")
    replies = relationship("Comment", remote_side=[comment_id]) # Self-referential

class CommentLike(Base):
    __tablename__ = "comment_likes" # [cite: 262]
    comment_id = Column(Integer, ForeignKey("comments.comment_id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)

# --- 4. Commerce & User Library ---
class Wishlist(Base):
    __tablename__ = "wishlists" # [cite: 288]
    wishlist_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="wishlist")
    book = relationship("Book")

class Cart(Base):
    __tablename__ = "carts" # [cite: 291]
    cart_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart")

class CartItem(Base):
    __tablename__ = "cart_items" # [cite: 264]
    cart_item_id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.cart_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False) # [cite: 269]
    created_at = Column(DateTime, default=func.now())

    cart = relationship("Cart", back_populates="items")
    book = relationship("Book")

class Library(Base):
    __tablename__ = "libraries" # [cite: 275]
    library_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    status = Column(Enum(LibraryStatus), default=LibraryStatus.READING) # [cite: 279]
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="library_books")
    book = relationship("Book")

class Order(Base):
    __tablename__ = "orders" # [cite: 297]
    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False) # [cite: 300]
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING) # [cite: 301]
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items" # [cite: 308]
    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    quantity = Column(Integer, nullable=False) # [cite: 313]
    price = Column(DECIMAL(10, 2), nullable=False) # [cite: 314]

    order = relationship("Order", back_populates="items")
    book = relationship("Book")

class TokenBlocklist(Base):
    __tablename__ = "token_blocklist"
    
    token = Column(String(500), primary_key=True) # 토큰 자체가 ID
    created_at = Column(DateTime, default=func.now())