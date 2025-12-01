# app/models/user.py
from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import generate_uuid

if TYPE_CHECKING:
    from app.models.subscription import Subscription
    from app.models.message_history import MessageHistory


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
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