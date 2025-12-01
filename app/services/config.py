import os
from dotenv import load_dotenv

# .env 로드
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_STANDARD_MODEL = os.getenv("OPENAI_STANDARD_MODEL", "gpt-4.1-mini")
OPENAI_PREMIUM_MODEL = os.getenv("OPENAI_PREMIUM_MODEL", "gpt-4.1")

if OPENAI_API_KEY is None:
    # 개발 중에 빨리 눈에 띄게 하려고 간단한 에러
    raise RuntimeError("OPENAI_API_KEY is not set. Please add it to your .env file.")