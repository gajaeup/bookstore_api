from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Wishlist, Book, User
from app.schemas import APIResponse, WishlistCreate, WishlistDto
from app.dependencies import get_current_user
from pydantic import BaseModel
class ErrorResponse(BaseModel):
    detail: str
common_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 요청"},
    401: {"model": ErrorResponse, "description": "인증 실패"},
    403: {"model": ErrorResponse, "description": "권한 없음"},
    404: {"model": ErrorResponse, "description": "찾을 수 없음"},
    500: {"model": ErrorResponse, "description": "서버 오류"},
}
router = APIRouter(responses=common_responses)

# 1. 위시리스트 추가
@router.post("/api/favorites", response_model=APIResponse)
def add_favorite(
    wish_req: WishlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 이미 추가했는지 확인
    exists = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.user_id,
        Wishlist.book_id == wish_req.book_id
    ).first()
    
    if exists:
        return APIResponse(isSuccess=False, message="이미 위시리스트에 존재합니다.")
    
    new_wish = Wishlist(user_id=current_user.user_id, book_id=wish_req.book_id)
    db.add(new_wish)
    db.commit()
    
    return APIResponse(isSuccess=True, message="위시리스트에 추가했습니다.")

# 2. 위시리스트 조회
@router.get("/api/favorites", response_model=APIResponse[list[WishlistDto]])
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wishes = db.query(Wishlist).filter(Wishlist.user_id == current_user.user_id).all()
    
    dtos = [
        WishlistDto(
            wishlist_id=w.wishlist_id,
            book_id=w.book_id,
            book_title=w.book.title,
            created_at=w.created_at.isoformat() if w.created_at else ""
        ) for w in wishes
    ]
    return APIResponse(isSuccess=True, message="위시리스트 조회 성공", payload=dtos)

# 3. 위시리스트 삭제
@router.delete("/api/favorites/{wishlist_id}", response_model=APIResponse)
def delete_favorite(
    wishlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wish = db.query(Wishlist).filter(
        Wishlist.wishlist_id == wishlist_id,
        Wishlist.user_id == current_user.user_id
    ).first()
    
    if not wish:
        return APIResponse(isSuccess=False, message="항목을 찾을 수 없습니다.")
        
    db.delete(wish)
    db.commit()
    return APIResponse(isSuccess=True, message="위시리스트에서 삭제했습니다.")