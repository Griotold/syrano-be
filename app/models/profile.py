# app/models/profile.py
from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Integer, Text, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import generate_uuid

if TYPE_CHECKING:
    from app.models.user import User


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=generate_uuid
    )
    
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # ✅ 핵심 정보만
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # ✅ SQLAlchemy 2.0 스타일: server_default 사용
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ✅ Relationship (양방향)
    user: Mapped["User"] = relationship(back_populates="profiles")

    # ✅ Index
    __table_args__ = (
        Index("idx_profiles_user_id", "user_id"),
    )