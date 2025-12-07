# app/db.py
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.services.config import DATABASE_URL, SQLALCHEMY_ECHO


class Base(DeclarativeBase):
    """모든 엔티티가 상속할 공통 Base."""
    pass


engine = create_async_engine(
    DATABASE_URL,
    echo=SQLALCHEMY_ECHO,      
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:  # 👈 여기 오타 조심 (괄호 필요)
        yield session


async def init_db() -> None:
    """
    앱 시작 시 한 번 테이블 생성.
    """
    # 이 import가 Base.metadata에 모델들을 등록하는 트리거 역할
    from app import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)