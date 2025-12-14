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
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pydantic import Field
from fastapi import Depends
from app.error_codes import ErrorCode
from datetime import datetime
class ErrorResponse(BaseModel):
    timestamp: str = Field(..., example="2025-12-14T12:00:00Z")
    path: str = Field(..., example="/api/request/url")
    status: int = Field(..., example=400)
    code: str = Field(..., example="ERROR_CODE")
    message: str = Field(..., example="에러 메시지")
    details: Optional[Dict[str, Any]] = Field(None, example={})


global_responses = {
    400: {
        "model": ErrorResponse,
        "description": "잘못된 요청 (Bad Request)",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2025-12-14T12:00:00Z",
                    "path": "/api/...",
                    "status": 400,
                    "code": "BAD_REQUEST",
                    "message": "입력값이 잘못되었습니다.",
                    "details": {"field": "value_error"}
                }
            }
        }
    },
    401: {
        "model": ErrorResponse,
        "description": "인증 실패 (Unauthorized)",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2025-12-14T12:00:00Z",
                    "path": "/api/auth/login",
                    "status": 401,
                    "code": "AUTH_FAILED",
                    "message": "인증 토큰이 없거나 유효하지 않습니다.",
                    "details": None
                }
            }
        }
    },
    403: {
        "model": ErrorResponse,
        "description": "권한 없음 (Forbidden)",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2025-12-14T12:00:00Z",
                    "path": "/api/admin/...",
                    "status": 403,
                    "code": "PERMISSION_DENIED",
                    "message": "접근 권한이 없습니다.",
                    "details": None
                }
            }
        }
    },
    404: {
        "model": ErrorResponse,
        "description": "찾을 수 없음 (Not Found)",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2025-12-14T12:00:00Z",
                    "path": "/api/books/999",
                    "status": 404,
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "요청한 리소스를 찾을 수 없습니다.",
                    "details": None
                }
            }
        }
    },
    405: {
        "model": ErrorResponse,
        "description": "허용되지 않은 메서드",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2025-12-14T12:00:00Z",
                    "path": "/api/...",
                    "status": 405,
                    "code": "METHOD_NOT_ALLOWED",
                    "message": "이 URL에서는 해당 HTTP 메서드를 지원하지 않습니다.",
                    "details": None
                }
            }
        }
    },
    409: {
        "model": ErrorResponse,
        "description": "데이터 충돌 (Conflict)",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2025-12-14T12:00:00Z",
                    "path": "/api/signup",
                    "status": 409,
                    "code": "DUPLICATE_RESOURCE",
                    "message": "이미 존재하는 데이터입니다 (예: 이메일 중복).",
                    "details": {"field": "email"}
                }
            }
        }
    },
    422: {
        "model": ErrorResponse,
        "description": "유효성 검사 실패",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2025-12-14T12:00:00Z",
                    "path": "/api/...",
                    "status": 422,
                    "code": "VALIDATION_ERROR",
                    "message": "입력값의 형식이 올바르지 않습니다.",
                    "details": {"email": "valid email required"}
                }
            }
        }
    },
    429: {
        "model": ErrorResponse,
        "description": "요청 한도 초과",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2025-12-14T12:00:00Z",
                    "path": "/api/...",
                    "status": 429,
                    "code": "TOO_MANY_REQUESTS",
                    "message": "요청 횟수가 너무 많습니다. 잠시 후 다시 시도해주세요.",
                    "details": None
                }
            }
        }
    },
    500: {
        "model": ErrorResponse,
        "description": "서버 내부 오류",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2025-12-14T12:00:00Z",
                    "path": "/api/...",
                    "status": 500,
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "서버 내부 오류가 발생했습니다.",
                    "details": None
                }
            }
        }
    },
    503: {
        "model": ErrorResponse,
        "description": "서비스 이용 불가",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2025-12-14T12:00:00Z",
                    "path": "/api/...",
                    "status": 503,
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "현재 서비스를 이용할 수 없습니다.",
                    "details": None
                }
            }
        }
    }
}
models.Base.metadata.create_all(bind=engine)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Bookstore API",
    version="1.0.0",
    description="과제 2 백엔드 API 서버",
    responses=global_responses
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
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Bookstore API",
        "version": "1.0.0",
        "status": "Healthy"  # <-- 이게 보이면 서버가 건강하다는 뜻!
    }

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