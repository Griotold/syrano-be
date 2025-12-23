import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_STANDARD_MODEL = os.getenv("OPENAI_STANDARD_MODEL", "gpt-4.1-mini")
OPENAI_PREMIUM_MODEL = os.getenv("OPENAI_PREMIUM_MODEL", "gpt-4.1")

DATABASE_URL = os.getenv("DATABASE_URL")
SQLALCHEMY_ECHO: bool = os.getenv("SQLALCHEMY_ECHO", "true").lower() == "true"

# Naver Clova OCR
NAVER_OCR_SECRET_KEY = os.getenv("NAVER_OCR_SECRET_KEY")
NAVER_OCR_INVOKE_URL = os.getenv("NAVER_OCR_INVOKE_URL")

if OPENAI_API_KEY is None:
    raise RuntimeError("OPENAI_API_KEY is not set. Please add it to your .env file.")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not set. Please add it to your .env file.")

# 로컬 개발 환경이면 SSL 비활성화 파라미터 추가
if "localhost" in DATABASE_URL or "127.0.0.1" in DATABASE_URL:
    if "ssl" not in DATABASE_URL.lower():
        separator = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL = f"{DATABASE_URL}{separator}ssl=disable"


if NAVER_OCR_SECRET_KEY is None:
    raise RuntimeError("NAVER_OCR_SECRET_KEY is not set. Please add it to your .env file.")

if NAVER_OCR_INVOKE_URL is None:
    raise RuntimeError("NAVER_OCR_INVOKE_URL is not set. Please add it to your .env file.")