# app/models/user.py
from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import generate_uuid

if TYPE_CHECKING:
    from app.models.subscription import Subscription
    from app.models.message_history import MessageHistory
    from app.models.profile import Profile  # ✅ 추가


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # User 1 : 1 Subscription
    subscription: Mapped["Subscription | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # User 1 : N MessageHistory
    messages: Mapped[list["MessageHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    # User 1 : N Profile ✅ 추가
    profiles: Mapped[list["Profile"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )