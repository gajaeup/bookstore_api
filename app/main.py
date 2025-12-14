# app/main.py
from fastapi import FastAPI, HTTPException, Request
from .database import engine
from . import models
from .routers import auth, users, books, reviews, carts, orders, wishlists, likes, stats
from .exceptions import global_exception_handler, custom_exception_handler, CustomException, validation_exception_handler, python_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import text
from fastapi import Depends
from app.error_codes import ErrorCode
from datetime import datetime
# 서버 시작 시 DB 테이블 자동 생성 (마이그레이션 도구 없이 초기 개발용)
models.Base.metadata.create_all(bind=engine)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Bookstore API",
    version="1.0.0",
    description="과제 2 백엔드 API 서버"
)
app.state.limiter = limiter

app.add_exception_handler(HTTPException, global_exception_handler)
app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, python_exception_handler)

app.include_router(auth.router, tags=["Auth (회원가입 / 로그인 / 로그아웃 / 토큰 재발급)"])
app.include_router(users.router, tags=["Users (사용자 관리)"])
app.include_router(books.router, tags=["Books (도서 관리)"])
app.include_router(reviews.router, tags=["Reviews (리뷰)"])
app.include_router(carts.router, tags=["Cart (장바구니)"])
app.include_router(orders.router, tags=["Orders (주문)"])
app.include_router(wishlists.router, tags=["Wishlists (위시리스트)"])
app.include_router(likes.router, tags=["Likes (좋아요)"])
app.include_router(stats.router, tags=["Stats (통계)"])

@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = "disconnected"
        logger.error(f"Health Check DB Error: {str(e)}")

    return {
        "status": "ok",
        "db_status": db_status,  # DB 상태 추가
        "version": "1.0.0",
        "build_timestamp": datetime.now().isoformat(),
        "maintainer": "Your Name"
    }
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 요청 로그
        logger.info(f"REQ: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 응답 로그
            logger.info(
                f"RES: {response.status_code} | Time: {process_time:.4f}s"
            )
            return response
        except Exception as e:
            # 에러 로그 (스택 트레이스)
            logger.error(f"ERROR: {str(e)}", exc_info=True)
            raise e

app.add_middleware(LoggingMiddleware)