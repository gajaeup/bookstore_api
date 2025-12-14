from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.database import get_db
from app.models import Book, User, UserRole
from app.schemas import APIResponse, BookCreate, BookDto, BookListResponse
from app.dependencies import get_current_user
import math
from app.schemas import BookCreate

router = APIRouter()

# 1. 도서 등록 (관리자 전용) [cite: 487]
@router.post("/api/admin/books", response_model=APIResponse)
def create_book(
    book_req: BookCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 관리자 권한 체크
    if current_user.role != UserRole.ADMIN:
        return APIResponse(isSuccess=False, message="관리자만 등록할 수 있습니다.")

    new_book = Book(
        title=book_req.title,
        author=book_req.author,
        publisher=book_req.publisher,
        summary=book_req.summary,
        price=book_req.price
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return APIResponse(isSuccess=True, message="도서 등록 성공", payload={"book_id": new_book.book_id})

# 2. 도서 목록 조회 (누구나 가능 - 검색/정렬/페이징) 
@router.get("/api/public/books", response_model=APIResponse[BookListResponse])
def get_books(
    page: int = 1,
    size: int = 10,
    search: str = None,
    sort: str = Query("created_at,desc", description="field,asc|desc"),
    db: Session = Depends(get_db)
):
    query = db.query(Book)

    # 검색 로직 (제목 또는 저자에 검색어가 포함되면)
    if search:
        query = query.filter(Book.title.contains(search) | Book.author.contains(search))

    # 정렬 로직
    sort_field, sort_dir = sort.split(",")
    if sort_dir.lower() == "desc":
        query = query.order_by(desc(getattr(Book, sort_field, Book.created_at)))
    else:
        query = query.order_by(asc(getattr(Book, sort_field, Book.created_at)))

    # 페이지네이션 계산
    total_count = query.count()
    total_pages = math.ceil(total_count / size)
    books = query.offset((page - 1) * size).limit(size).all()

    # Pydantic 모델로 변환
    book_dtos = [BookDto.model_validate(b) for b in books]
    
    return APIResponse(
        isSuccess=True,
        message="도서 목록 조회 성공",
        payload={
            "content": book_dtos,
            "pagination": {
                "totalCount": total_count,
                "page": page,
                "size": size,
                "totalPages": total_pages
            }
        }
    )

# 3. 도서 상세 조회 [cite: 548]
@router.get("/api/public/books/{book_id}", response_model=APIResponse[BookDto])
def get_book_detail(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        return APIResponse(isSuccess=False, message="도서를 찾을 수 없습니다.")
    
    dto = BookDto.model_validate(book)
    if book.created_at:
        dto.created_at = book.created_at.isoformat()

    return APIResponse(isSuccess=True, message="도서 상세 조회 성공", payload=dto)

@router.patch("/api/admin/books/{book_id}", response_model=APIResponse)
def update_book(
    book_id: int,
    book_req: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        return APIResponse(isSuccess=False, message="권한이 없습니다.")
    
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        return APIResponse(isSuccess=False, message="도서를 찾을 수 없습니다.")
    
    # 필드 업데이트
    book.title = book_req.title
    book.author = book_req.author
    book.publisher = book_req.publisher
    book.price = book_req.price
    book.summary = book_req.summary
    
    db.commit()
    return APIResponse(isSuccess=True, message="도서 정보를 수정했습니다.")

# [Admin] 5. 도서 삭제 (관리자 전용)
@router.delete("/api/admin/books/{book_id}", response_model=APIResponse)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        return APIResponse(isSuccess=False, message="권한이 없습니다.")
    
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        return APIResponse(isSuccess=False, message="도서를 찾을 수 없습니다.")
    
    db.delete(book)
    db.commit()
    return APIResponse(isSuccess=True, message="도서를 삭제했습니다.")