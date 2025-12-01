# app/models/message_history.py
from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import generate_uuid

if TYPE_CHECKING:
    from app.models.user import User


class MessageHistory(Base):
    __tablename__ = "message_history"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    conversation: Mapped[str] = mapped_column(Text)

    suggestions: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    user: Mapped["User"] = relationship(back_populates="messages")