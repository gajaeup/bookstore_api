from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, APIResponse, Token
from app.utils import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import TokenBlocklist
import jwt
from pydantic import BaseModel
from app.exceptions import CustomException
from app.error_codes import ErrorCode
from app.config import SECRET_KEY, ALGORITHM
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

# 1. 회원가입 API
@router.post("/api/signup", response_model=APIResponse, summary="회원가입")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 체크
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        return APIResponse(isSuccess=False, message="이미 존재하는 이메일입니다.")
    
    # 사용자 생성
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        password=hashed_password,
        username=user.username,
        role="USER"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return APIResponse(
        isSuccess=True, 
        message="회원가입 성공", 
        payload={"user_id": new_user.user_id}
    )

# 2. 로그인 API
@router.post("/api/auth/login", response_model=APIResponse, summary="로그인")
def login(user_req: UserLogin, db: Session = Depends(get_db)):
    # 사용자 확인
    user = db.query(User).filter(User.email == user_req.email).first()
    if not user or not verify_password(user_req.password, user.password):
        raise CustomException(ErrorCode.LOGIN_FAILED)
    
    # 토큰 발급
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=30))
    refresh_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(days=7))
    
    return APIResponse(
        isSuccess=True,
        message="로그인 성공",
        payload={
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": {
                "user_id": user.user_id,
                "role": user.role,
                "token_type": "Bearer"
            }
        }
    )

security = HTTPBearer()

# 3. 로그아웃
@router.post("/api/auth/logout", response_model=APIResponse, summary="로그아웃")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials # Bearer 뒤의 토큰 값만 추출
    
    # 이미 블랙리스트에 있는지 확인 (중복 방지)
    exists = db.query(TokenBlocklist).filter(TokenBlocklist.token == token).first()
    if exists:
         return APIResponse(isSuccess=True, message="이미 로그아웃된 토큰입니다.")

    # 블랙리스트에 추가
    blocked_token = TokenBlocklist(token=token)
    db.add(blocked_token)
    db.commit()
    
    return APIResponse(isSuccess=True, message="로그아웃 되었습니다.")

# 4. 토큰 갱신 (Refresh Token)
class RefreshTokenReq(BaseModel):
    refreshToken: str

@router.post("/api/auth/refresh", response_model=APIResponse, summary="토큰 재발급")
def refresh_token(
    req: RefreshTokenReq,
    db: Session = Depends(get_db)
):
    # 리프레시 토큰 검증
    try:
        payload = jwt.decode(req.refreshToken, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise CustomException(ErrorCode.INVALID_TOKEN)
            
        # 블랙리스트 체크 (선택 사항이지만 보안상 권장)
        if db.query(TokenBlocklist).filter(TokenBlocklist.token == req.refreshToken).first():
             raise CustomException(ErrorCode.LOGOUT_TOKEN)

    except jwt.PyJWTError:
        raise CustomException(ErrorCode.EXPIRED_TOKEN)
    
    # 새 액세스 토큰 발급
    access_token = create_access_token(data={"sub": email}, expires_delta=timedelta(minutes=30))
    
    return APIResponse(
        isSuccess=True, 
        message="토큰이 재발급되었습니다.", 
        payload={
            "accessToken": access_token,
            "refreshToken": req.refreshToken, # 기존 것 유지 또는 재발급
            "token_type": "Bearer"
        }
    )