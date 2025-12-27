# app/models/subscription.py
from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime, date

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import generate_uuid

if TYPE_CHECKING:
    from app.models.user import User


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    # 유저당 구독 1개만 허용 (UNIQUE)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        unique=True,
    )

    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    # weekly, monthly
    plan_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    daily_usage_count: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        nullable=False
    )
    last_reset_date: Mapped[date | None] = mapped_column(
        Date, 
        nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="subscription")