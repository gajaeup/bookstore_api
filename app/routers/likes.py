from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Review, ReviewLike, User
from app.schemas import APIResponse
from app.dependencies import get_current_user
from app.exceptions import CustomException
from app.error_codes import ErrorCode
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

@router.post("/api/reviews/{review_id}/like", response_model=APIResponse)
def like_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 이미 좋아요 했는지 확인
    exists = db.query(ReviewLike).filter(
        ReviewLike.review_id == review_id, 
        ReviewLike.user_id == current_user.user_id
    ).first()
    
    if exists:
        raise CustomException(ErrorCode.ALREADY_EXISTS)
    
    # 좋아요 추가 및 카운트 증가
    db.add(ReviewLike(review_id=review_id, user_id=current_user.user_id))
    review = db.query(Review).filter(Review.review_id == review_id).first()
    review.likes += 1
    db.commit()
    
    return APIResponse(isSuccess=True, message="좋아요를 등록했습니다.", payload={"likes": review.likes})

@router.delete("/api/reviews/{review_id}/like", response_model=APIResponse)
def unlike_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    like_obj = db.query(ReviewLike).filter(
        ReviewLike.review_id == review_id, 
        ReviewLike.user_id == current_user.user_id
    ).first()
    
    if not like_obj:
        raise CustomException(ErrorCode.RESOURCE_NOT_FOUND)
    
    db.delete(like_obj)
    review = db.query(Review).filter(Review.review_id == review_id).first()
    review.likes -= 1
    db.commit()
    
    return APIResponse(isSuccess=True, message="좋아요를 취소했습니다.", payload={"likes": review.likes})