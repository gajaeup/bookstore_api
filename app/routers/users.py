# app/routers/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import APIResponse
from app.dependencies import get_current_user
from app.models import User
from pydantic import BaseModel
from datetime import datetime
from app.models import UserRole
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

# [cite_start]내 정보 조회 (API 명세서 5번 기능) [cite: 113, 115]
@router.get("/api/users/me", response_model=APIResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return APIResponse(
        isSuccess=True,
        message="내 정보를 조회합니다.",
        payload={
            "user_id": current_user.user_id,
            "email": current_user.email,
            "username": current_user.username,
            "role": current_user.role,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        }
    )

class UserUpdate(BaseModel):
    username: str

# 2. 내 정보 수정
@router.patch("/api/users/me", response_model=APIResponse)
def update_my_info(
    user_req: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.username = user_req.username
    db.commit()
    return APIResponse(isSuccess=True, message="정보를 수정했습니다.", payload={"username": current_user.username})

# 3. 회원 탈퇴 (Soft Delete)
@router.delete("/api/users/me", response_model=APIResponse)
def withdraw(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.deleted_at:
            return APIResponse(isSuccess=False, message="이미 탈퇴한 회원입니다.")

        # 현재 시간 기록 (이게 있으면 탈퇴한 것으로 간주)
    current_user.deleted_at = datetime.now()
    db.commit()
    return APIResponse(isSuccess=True, message="회원 탈퇴 처리되었습니다.")

# [Admin] 6. 유저 영구 삭제 (관리자 전용)
@router.delete("/api/admin/users/{user_id}", response_model=APIResponse)
def hard_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 관리자 권한 체크
    if current_user.role != UserRole.ADMIN:
        return APIResponse(isSuccess=False, message="관리자만 수행할 수 있습니다.")

    # 삭제할 유저 찾기
    target_user = db.query(User).filter(User.user_id == user_id).first()
    if not target_user:
        return APIResponse(isSuccess=False, message="사용자를 찾을 수 없습니다.")

    # [주의] 진짜로 DB에서 날려버림
    db.delete(target_user)
    db.commit()
    
    return APIResponse(isSuccess=True, message=f"유저(ID: {user_id})를 영구 삭제했습니다.")