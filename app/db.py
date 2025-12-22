# app/db.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import DATABASE_URL, SQLALCHEMY_ECHO

class Base(DeclarativeBase):
    """모든 엔티티가 상속할 공통 Base."""
    pass

# 로컬 환경이면 SSL 비활성화, 프로덕션이면 SSL 활성화
connect_args = {}
if "localhost" in DATABASE_URL or "127.0.0.1" in DATABASE_URL:
    connect_args = {"ssl": False}
else:
    connect_args = {"ssl": "require"}

engine = create_async_engine(
    DATABASE_URL,
    echo=SQLALCHEMY_ECHO,
    future=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def init_db() -> None:
    """
    앱 시작 시 한 번 테이블 생성.
    """
    from app import models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)