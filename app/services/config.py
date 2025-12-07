import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_STANDARD_MODEL = os.getenv("OPENAI_STANDARD_MODEL", "gpt-4.1-mini")
OPENAI_PREMIUM_MODEL = os.getenv("OPENAI_PREMIUM_MODEL", "gpt-4.1")

DATABASE_URL = os.getenv("DATABASE_URL")
SQLALCHEMY_ECHO: bool = os.getenv("SQLALCHEMY_ECHO", "true").lower() == "true"

if OPENAI_API_KEY is None:
    raise RuntimeError("OPENAI_API_KEY is not set. Please add it to your .env file.")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not set. Please add it to your .env file.")