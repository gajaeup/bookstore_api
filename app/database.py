# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# .env 파일에 DB_URL="mysql+pymysql://아이디:비밀번호@JCloud주소:포트/DB이름" 형식으로 저장해야 함
SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL", "mysql+pymysql://root:password@localhost:3306/bookstore")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency (API에서 DB 세션을 쓰기 위함)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  