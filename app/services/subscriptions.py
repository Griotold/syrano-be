# app/services/subscriptions.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone, date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models import Subscription
from app.schemas.rizz import UsageInfo


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


async def check_and_increment_usage(
    session: AsyncSession,
    user_id: str,
) -> UsageInfo:
    """
    사용량 체크 및 증가
    
    1. 오늘 날짜 확인
    2. last_reset_date와 비교 → 다르면 카운터 리셋
    3. 무료 사용자면 5회 제한 체크
    4. 카운터 +1
    5. 사용량 정보 반환
    
    Returns:
        UsageInfo: 남은 횟수, 제한, 프리미엄 여부
        
    Raises:
        HTTPException(429): 무료 사용자 일일 한도 초과
        HTTPException(404): 구독 정보 없음
    """
    # 1. Subscription 조회
    subscription = await get_subscription_by_user_id(session, user_id)
    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="구독 정보를 찾을 수 없어요.",
        )
    
    today = date.today()
    
    # 2. 날짜 체크 및 리셋
    if subscription.last_reset_date != today:
        # 새로운 날 → 카운터 리셋
        subscription.daily_usage_count = 0
        subscription.last_reset_date = today
    
    # 3. 무료 사용자 제한 체크 (증가 전에 체크)
    if not subscription.is_premium and subscription.daily_usage_count >= 5:
        raise HTTPException(
            status_code=429,
            detail="오늘의 무료 사용 횟수를 모두 사용했어요. 프리미엄으로 업그레이드하거나 내일 다시 시도해주세요!",
        )
    
    # 4. 카운터 증가
    subscription.daily_usage_count += 1
    
    # 5. DB 커밋
    await session.commit()
    await session.refresh(subscription)
    
    # 6. 사용량 정보 반환
    if subscription.is_premium:
        return UsageInfo(
            remaining=-1,  # 무제한
            limit=-1,
            is_premium=True,
        )
    else:
        return UsageInfo(
            remaining=5 - subscription.daily_usage_count,
            limit=5,
            is_premium=False,
        )