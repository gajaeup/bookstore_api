from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Review, User, Book
from app.schemas import APIResponse, ReviewCreate, ReviewDto, ReviewListResponse, ReviewUpdate
from app.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pydantic import Field
class ErrorResponse(BaseModel):
    timestamp: str = Field(..., example="2025-12-14T12:00:00Z")
    path: str = Field(..., example="/api/request/url")
    status: int = Field(..., example=400)
    code: str = Field(..., example="ERROR_CODE_EXAMPLE")
    message: str = Field(..., example="에러 메시지가 여기에 나옵니다.")
    details: Optional[Dict[str, Any]] = Field(None, example={"field": "error_detail"})

common_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 요청"},
    401: {"model": ErrorResponse, "description": "인증 실패"},
    403: {"model": ErrorResponse, "description": "권한 없음"},
    404: {"model": ErrorResponse, "description": "찾을 수 없음"},
    500: {"model": ErrorResponse, "description": "서버 오류"},
}
router = APIRouter(responses=common_responses)

# 1. 리뷰 작성 (로그인 필수)
@router.post("/api/books/{book_id}/reviews", response_model=APIResponse)
def create_review(
    book_id: int,
    review_req: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 책이 진짜 있는지 확인
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        return APIResponse(isSuccess=False, message="존재하지 않는 도서입니다.")

    # 리뷰 저장
    new_review = Review(
        user_id=current_user.user_id,
        book_id=book_id,
        rating=review_req.rating,
        content=review_req.content
    )
    db.add(new_review)
    db.commit()
    
    return APIResponse(isSuccess=True, message="리뷰가 작성되었습니다.")

# 2. 특정 도서의 리뷰 목록 조회 (누구나 가능)
@router.get("/api/books/{book_id}/reviews", response_model=APIResponse[ReviewListResponse])
def get_book_reviews(book_id: int, db: Session = Depends(get_db)):
    # 최신순 정렬
    reviews = db.query(Review).filter(Review.book_id == book_id).order_by(Review.created_at.desc()).all()
    
    # DTO 변환 (User 정보 포함)
    review_dtos = []
    for r in reviews:
        dto = ReviewDto(
            review_id=r.review_id,
            user_id=r.user_id,
            username=r.user.username, # 관계형 데이터(User) 접근
            rating=r.rating,
            content=r.content,
            created_at=r.created_at.isoformat() if r.created_at else ""
        )
        review_dtos.append(dto)

    return APIResponse(
        isSuccess=True,
        message="리뷰 목록 조회 성공",
        payload={
            "content": review_dtos,
            "totalCount": len(review_dtos)
        }
    )
@router.get("/api/reviews/me", response_model=APIResponse[list[ReviewDto]])
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reviews = db.query(Review).filter(Review.user_id == current_user.user_id).all()
    
    # DTO 변환
    review_dtos = [
        ReviewDto(
            review_id=r.review_id,
            user_id=r.user_id,
            username=r.user.username,
            rating=r.rating,
            content=r.content,
            created_at=r.created_at.isoformat() if r.created_at else ""
        ) for r in reviews
    ]
    return APIResponse(isSuccess=True, message="내 리뷰 목록 조회 성공", payload=review_dtos)

# 4. 리뷰 수정
@router.patch("/api/reviews/{review_id}", response_model=APIResponse)
def update_review(
    review_id: int,
    review_req: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(Review).filter(Review.review_id == review_id).first()
    if not review:
        return APIResponse(isSuccess=False, message="리뷰를 찾을 수 없습니다.")
    
    # 작성자 본인 확인
    if review.user_id != current_user.user_id:
        return APIResponse(isSuccess=False, message="수정 권한이 없습니다.")

    if review_req.rating:
        review.rating = review_req.rating
    if review_req.content:
        review.content = review_req.content
    
    db.commit()
    return APIResponse(isSuccess=True, message="리뷰를 수정했습니다.")

# 5. 리뷰 삭제
@router.delete("/api/reviews/{review_id}", response_model=APIResponse)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(Review).filter(Review.review_id == review_id).first()
    if not review:
        return APIResponse(isSuccess=False, message="리뷰를 찾을 수 없습니다.")
    
    # 작성자 본인 확인 (관리자도 삭제 가능하게 하려면 OR 조건 추가)
    if review.user_id != current_user.user_id and current_user.role != "ADMIN":
        return APIResponse(isSuccess=False, message="삭제 권한이 없습니다.")

    db.delete(review)
    db.commit()
    return APIResponse(isSuccess=True, message="리뷰를 삭제했습니다.")