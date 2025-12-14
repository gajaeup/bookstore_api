import os
from dotenv import load_dotenv

load_dotenv()
# 임시 비밀키 (나중엔 .env로 옮기세요)
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_1234")
ALGORITHM = "HS256"
