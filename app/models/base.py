import uuid

from app.db import Base


def generate_uuid() -> str:
    """UUID 문자열 생성 헬퍼."""
    return str(uuid.uuid4())