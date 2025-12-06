# app/services/subscriptions.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Subscription


async def get_subscription_by_user_id(
    session: AsyncSession,
    user_id: str,
) -> Subscription | None:
    result = await session.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def activate_subscription(
    session: AsyncSession,
    user_id: str,
    plan_type: str,
) -> Subscription:
    """
    주어진 user_id에 대해 프리미엄 구독을 활성화한다.
    - plan_type: "weekly" 또는 "monthly"
    - expires_at: 단순히 7일/30일 뒤로 설정 (MVP 용도)
    """
    # 만료일 계산 (UTC 기준)
    now = datetime.now(timezone.utc)

    if plan_type == "weekly":
        expires_at = now + timedelta(days=7)
    elif plan_type == "monthly":
        expires_at = now + timedelta(days=30)
    else:
        # MVP라 단순하게 처리 - 나중에 plan 정의를 enum/테이블로 분리해도 됨
        raise ValueError(f"Unsupported plan_type: {plan_type}")

    # 기존 구독 가져오기
    subscription = await get_subscription_by_user_id(session, user_id)

    # 없으면 새로 생성 (이론상은 항상 있지만, 방어적으로 처리)
    if subscription is None:
        subscription = Subscription(
            user_id=user_id,
        )
        session.add(subscription)

    subscription.is_premium = True
    subscription.plan_type = plan_type
    subscription.expires_at = expires_at

    await session.commit()
    await session.refresh(subscription)

    return subscription