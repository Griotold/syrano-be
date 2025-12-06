from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Subscription


async def get_subscription_by_user_id(
    session: AsyncSession,
    user_id: str,
) -> Subscription | None:
    """user_id로 현재 구독 상태를 조회한다."""
    result = await session.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    return result.scalar_one_or_none()