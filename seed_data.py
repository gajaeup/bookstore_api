# seed_data.py (수정본)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Book, User, Review
from app.utils import get_password_hash
# get_db 대신 SessionLocal을 가져와야 합니다!
from app.database import SessionLocal 
import random

def init_db():
    print("🌱 데이터 생성을 시작합니다...")
    
    # 1. 세션 생성 (이걸로 끝까지 씁니다)
    db = SessionLocal()

    try:
        # 1. 유저 10명 생성
        print("👤 유저 생성 중...")
        for i in range(10):
            # 중복 방지 체크
            email = f"user{i}@example.com"
            if not db.query(User).filter(User.email == email).first():
                user = User(
                    email=email,
                    password=get_password_hash("password123"),
                    username=f"User{i}",
                    role="USER"
                )
                db.add(user)
        db.commit()
        print("✅ 유저 생성 완료")

        # 2. 도서 200권 생성
        print("📚 도서 생성 중...")
        # 도서가 비어있을 때만 넣기 (선택사항)
        if db.query(Book).count() == 0:
            for i in range(200):
                book = Book(
                    title=f"테스트 도서 {i}",
                    author=f"저자 {i}",
                    publisher=f"출판사 {i}",
                    price=random.randint(10000, 50000),
                    summary=f"이 책은 {i}번째 테스트 도서입니다.",
                )
                db.add(book)
            db.commit()
            print("✅ 도서 100권 생성 완료")
        else:
            print("ℹ️ 도서 데이터가 이미 있습니다.")

        # 3. 리뷰 100개 생성
        print("✍️ 리뷰 생성 중...")
        # 유저와 도서 ID 범위 확인을 위해 실제 DB에서 가져오기
        users = db.query(User).all()
        books = db.query(Book).all()

        if users and books:
            for i in range(100):
                review = Review(
                    user_id=random.choice(users).user_id, # 존재하는 유저 중 랜덤
                    book_id=random.choice(books).book_id, # 존재하는 책 중 랜덤
                    rating=random.randint(1, 5),
                    content=f"정말 좋은 책 {i}입니다!"
                )
                db.add(review)
            db.commit()
            print("✅ 리뷰 100개 생성 완료")
        
        print("🎉 총 210개 데이터 생성 끝!")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        db.rollback() # 에러나면 되돌리기
    finally:
        db.close() # 꼭 닫아주기

if __name__ == "__main__":
    init_db()