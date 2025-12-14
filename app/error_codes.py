

class ErrorCode:
    # 400 Bad Request
    INVALID_INPUT_VALUE = ("C001", "입력값이 올바르지 않습니다.", 400)
    OUT_OF_STOCK = ("O001", "재고가 부족합니다.", 400) # 주문 시 사용 예정

    # 401 Unauthorized
    LOGIN_FAILED = ("A001", "이메일 또는 비밀번호가 일치하지 않습니다.", 401)
    INVALID_TOKEN = ("A002", "유효하지 않은 토큰입니다.", 401)
    EXPIRED_TOKEN = ("A003", "만료된 토큰입니다.", 401)
    LOGOUT_TOKEN = ("A004", "로그아웃된 토큰입니다.", 401)

    # 403 Forbidden
    ACCESS_DENIED = ("A005", "접근 권한이 없습니다.", 403)

    # 404 Not Found
    RESOURCE_NOT_FOUND = ("C002", "리소스를 찾을 수 없습니다.", 404)

    # 409 Conflict
    EMAIL_DUPLICATION = ("U001", "이미 존재하는 이메일입니다.", 409)
    ALREADY_EXISTS = ("C003", "이미 등록된 리소스입니다.", 409)

    # 422 Unprocessable Entity
    VALIDATION_ERROR = ("C004", "요청 형식이 유효하지 않습니다.", 422)

    # 429 Too Many Requests
    TOO_MANY_REQUESTS = ("G001", "요청 횟수가 너무 많습니다. 잠시 후 시도해주세요.", 429)

    # 500 Internal Server Error
    INTERNAL_SERVER_ERROR = ("S001", "서버 내부 오류입니다.", 500)

    # 503 Service Unavailable
    DB_CONNECTION_ERROR = ("S002", "데이터베이스 연결에 실패했습니다.", 503) # 헬스체크 시 사용 예정