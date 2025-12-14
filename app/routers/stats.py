from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Order, Book, UserRole
from app.schemas import APIResponse
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

@router.get("/api/admin/stats/users", summary="총 유저 수 조회 (관리자)")
def get_user_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        return APIResponse(isSuccess=False, message="권한이 없습니다.")
    count = db.query(User).count()
    return APIResponse(isSuccess=True, message="성공", payload={"total_users": count})

@router.get("/api/admin/stats/sales", summary="총 매출 조회 (관리자)")
def get_sales_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        return APIResponse(isSuccess=False, message="권한이 없습니다.")
    total = db.query(func.sum(Order.total_amount)).scalar() or 0
    return APIResponse(isSuccess=True, message="성공", payload={"total_sales": float(total)})

@router.get("/api/admin/stats/books", summary="총 도서 수 조회 (관리자)")
def get_book_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        return APIResponse(isSuccess=False, message="권한이 없습니다.")
    count = db.query(Book).count()
    return APIResponse(isSuccess=True, message="성공", payload={"total_books": count})