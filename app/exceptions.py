from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from fastapi.exceptions import RequestValidationError
from app.error_codes import ErrorCode

class CustomException(Exception):
    def __init__(self, error_code):
        # error_code가 튜플/리스트인 경우와 객체인 경우 모두 처리
        if isinstance(error_code, (list, tuple)):
            self.code = error_code[0]
            self.message = error_code[1]
            self.status_code = error_code[2]
        else:
            self.code = getattr(error_code, "code", "ERROR")
            self.message = getattr(error_code, "message", "Error occurred")
            self.status_code = getattr(error_code, "status_code", 400)

def create_error_response(status_code: int, code: str, message: str, path: str, details: dict = None):
    return JSONResponse(
        status_code=status_code,
        content={
            "timestamp": datetime.now().isoformat(),
            "path": path,
            "status": status_code,
            "code": code,
            "message": message,
            "details": details or {}
        }
    )

# 1. 일반적인 HTTP 에러 처리 (404 Not Found 등)
async def global_exception_handler(request: Request, exc: HTTPException):
    # 상태 코드에 따른 대표 에러 코드 매핑 (과제 요건 충족용)
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "RESOURCE_NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR"
    }
    error_code = code_map.get(exc.status_code, "ERROR")
    
    return create_error_response(
        status_code=exc.status_code,
        code=error_code,
        message=str(exc.detail),
        path=str(request.url.path)
    )

# 2. 커스텀 비즈니스 로직 에러 처리
async def custom_exception_handler(request: Request, exc: CustomException):
    return create_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        path=str(request.url.path)
    )

# 3. [중요!] 유효성 검사(Validation) 에러 처리 (422) - 이게 빠져있었습니다!
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = {}
    for error in exc.errors():
        # 에러 발생 필드 위치 찾기 (body -> email 등)
        loc = error["loc"][-1] if error["loc"] else "unknown"
        details[str(loc)] = error["msg"]
        
    return create_error_response(
        status_code=422,
        code="VALIDATION_FAILED",
        message="입력값이 유효하지 않습니다.",
        path=str(request.url.path),
        details=details
    )

# 4. [중요!] 그 외 알 수 없는 서버 에러 처리 (500)
async def python_exception_handler(request: Request, exc: Exception):
    return create_error_response(
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message="서버 내부 오류가 발생했습니다.",
        path=str(request.url.path),
        details={"error": str(exc)} # 실제 배포시는 보안상 제외하지만 과제 검증용 포함
    )