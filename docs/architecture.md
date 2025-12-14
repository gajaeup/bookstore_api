# 🏗️ Bookstore API Architecture

## 1. 기술 스택 (Tech Stack)

| 구분           | 기술 / 도구    | 설명                                  |
| :------------- | :------------- | :------------------------------------ |
| **Language**   | Python 3.12+   | 핵심 개발 언어                        |
| **Framework**  | FastAPI        | 비동기 고성능 웹 프레임워크           |
| **Server**     | Uvicorn        | ASGI 웹 서버 구현체                   |
| **Database**   | MySQL 8.0      | 관계형 데이터베이스 (RDBMS)           |
| **ORM**        | SQLAlchemy     | Python Object-Relational Mapping      |
| **Validation** | Pydantic       | 데이터 유효성 검사 및 설정 관리       |
| **Auth**       | PyJWT, Passlib | JWT 토큰 발급 및 Bcrypt 비밀번호 해싱 |
| **Deployment** | Systemd        | 리눅스 서비스 등록 및 프로세스 관리   |

---

## 2. 프로젝트 디렉토리 구조 (Directory Structure)

```text
bookstore/
├── app/
│   ├── __init__.py
│   ├── main.py              # 애플리케이션 진입점 (Entry Point)
│   ├── database.py          # DB 연결 세션 및 엔진 설정
│   ├── models.py            # SQLAlchemy DB 모델 정의 (ORM)
│   ├── schemas.py           # Pydantic 데이터 검증 스키마 (DTO)
│   ├── exceptions.py        # 커스텀 에러 핸들러 및 예외 정의
│   ├── utils.py             # 비밀번호 해싱 등 유틸리티 함수
│   └── routers/             # API 엔드포인트 라우터 모음
│       ├── __init__.py
│       ├── auth.py          # 인증 (로그인/회원가입/토큰)
│       ├── users.py         # 사용자 관리
│       ├── books.py         # 도서 관리 (검색/필터)
│       ├── reviews.py       # 리뷰 및 평점
│       ├── carts.py         # 장바구니
│       ├── orders.py        # 주문 처리
│       ├── wishlists.py     # 위시리스트
│       ├── likes.py         # 좋아요 기능
│       └── stats.py         # 관리자 통계
├── tests/                   # 테스트 코드 디렉토리
│   ├── __init__.py
│   └── test_api.py          # 통합 테스트 시나리오
├── .env.example             # 환경 변수 예시 파일
├── requirements.txt         # 의존성 패키지 목록
├── seed_data.py             # 초기 더미 데이터 생성 스크립트
├── reset_db.py              # DB 초기화 스크립트
├── bookstore.service        # Systemd 배포 설정 파일
└── architecture.md          # 시스템 아키텍처 문서
```

---

## 3. 계층 아키텍처

코드 스니펫

graph TD
Client[Client (Web/Postman)] -->|HTTP Request| Middleware[Logging/CORS Middleware]
Middleware -->|Router Dispatch| Presentation[Presentation Layer<br>(Routers)]
Presentation -->|Dependency Injection| Service[Service/Business Logic<br>(Embedded in Routers)]
Service -->|DTO/Schema| DataAccess[Data Access Layer<br>(SQLAlchemy ORM)]
DataAccess -->|SQL Query| DB[(MySQL Database)]

    subgraph Shared Components
        Auth[Auth Dependency<br>(JWT/Security)]
        Exceptions[Global Exception Handler]
        Models[DB Models]
        Schemas[Pydantic Schemas]
    end

    Presentation -.-> Auth
    Presentation -.-> Exceptions
    DataAccess -.-> Models

### 3.1. 계층별 역할

Presentation Layer (routers/):

HTTP 요청을 수신하고 응답을 반환합니다.

URL 경로와 HTTP 메서드(GET, POST 등)를 매핑합니다.

Pydantic 스키마를 사용하여 요청 데이터(Body, Query)를 1차 검증합니다.

Service/Logic Layer:

현재 구조에서는 라우터 내부 및 utils.py에 비즈니스 로직이 구현되어 있습니다.

사용자 권한 확인, 비밀번호 검증, 데이터 가공 등을 수행합니다.

Data Access Layer (models.py, database.py):

SQLAlchemy를 통해 데이터베이스와 직접 통신합니다.

ORM을 사용하여 SQL 쿼리 없이 Python 객체로 데이터를 조작합니다.

---

## 4. 데이터 흐름 및 의존성 (Dependencies)

### 4.1. 요청 처리 흐름 (Request Lifecycle)

Request: 클라이언트가 API를 호출합니다.

Middleware: 로깅 미들웨어가 요청 시간과 경로를 기록합니다.

Dependency: get_db가 DB 세션을 생성하고, get_current_user가 JWT 토큰을 검증하여 사용자 정보를 주입합니다.

Validation: Pydantic Schema가 입력값의 타입과 필수 여부를 검사합니다.

Logic & DB: 라우터가 로직을 수행하고 ORM을 통해 DB 데이터를 조회/수정합니다.

Response: 결과를 Pydantic Schema 또는 JSON으로 변환하여 반환합니다.

Exception: 에러 발생 시 global_exception_handler가 표준화된 에러 응답을 생성합니다.

### 4.2. 핵심 모듈 간 의존성

Routers는 Schemas와 Models에 의존합니다.

Models는 Database 설정(Base)에 의존합니다.

Auth 모듈은 Models(User)와 Utils(Passlib)에 의존합니다.

---

## 5. 데이터베이스 설계 개요

주요 리소스 간의 관계는 다음과 같습니다.

User (1) : (N) Order - 사용자는 여러 주문을 할 수 있습니다.

User (1) : (N) Review - 사용자는 여러 리뷰를 작성할 수 있습니다.

Book (1) : (N) Review - 책은 여러 리뷰를 가질 수 있습니다.

Cart (1) : (N) CartItem - 장바구니는 여러 아이템을 담습니다.

Book (N) : (M) Category - 책은 여러 카테고리에 속할 수 있습니다 (다대다).

---

## 6. 배포 아키텍처

Process Manager: Systemd를 사용하여 OS 부팅 시 자동 실행 및 프로세스 재시작을 보장합니다.

Environment: .env 파일을 통해 민감한 정보(DB 접속 정보, Secret Key)를 분리하여 관리합니다.

Logging: logging 모듈을 통해 표준 출력(stdout) 및 파일로 로그를 남기며, nohup 또는 journalctl로 관리됩니다.

[User Request]
⬇
[JCloud Firewall/Port Forwarding]
⬇
[Uvicorn Server (Port 8080)] <--(Systemd Managed)
⬇
[FastAPI Application]
⬇
[MySQL Database (Port 3306)]
