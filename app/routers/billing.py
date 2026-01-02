from __future__ import annotations

import logging
from datetime import datetime, date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.services.subscriptions import (
    activate_subscription,
    get_subscription_by_user_id,
    check_and_update_subscription_status,  # ✅ 추가
)

logger = logging.getLogger("syrano")
router = APIRouter()


class SubscribeRequest(BaseModel):
    user_id: str
    plan_type: Literal["weekly", "monthly"]
    transaction_id: str | None = None  # ← 추가 (선택)
    platform: str | None = None  # ← 추가 (선택)


class SubscriptionStatusResponse(BaseModel):
    user_id: str
    is_premium: bool
    plan_type: str | None = None
    expires_at: datetime | None = None


class UsageResponse(BaseModel):  # ✅ 추가
    """사용량 조회 응답"""
    is_premium: bool
    remaining_count: int | None  # None: 무제한
    daily_limit: int | None      # None: 무제한
    used_count: int              # 오늘 사용한 횟수


@router.post("/subscribe", response_model=SubscriptionStatusResponse)
async def subscribe(
    body: SubscribeRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    프리미엄 구독 활성화 엔드포인트 (MVP용).
    - 실제 앱 스토어 결제 검증은 나중에 별도로 붙일 예정.
    """
    try:
        subscription = await activate_subscription(
            session=session,
            user_id=body.user_id,
            plan_type=body.plan_type,
            transaction_id=body.transaction_id,  # ← 추가
            platform=body.platform,  # ← 추가
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception:
        logger.exception("Failed to activate subscription")
        raise HTTPException(
            status_code=500,
            detail="구독을 활성화하는 중 오류가 발생했어요.",
        )

    return SubscriptionStatusResponse(
        user_id=subscription.user_id,
        is_premium=subscription.is_premium,
        plan_type=subscription.plan_type,
        expires_at=subscription.expires_at,
    )


@router.get("/usage", response_model=UsageResponse)  # ✅ 추가
async def get_usage(
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    사용자의 현재 사용량 조회
    
    - 프리미엄: remaining_count=None, daily_limit=None (무제한)
    - 무료: remaining_count=0~5, daily_limit=5
    - 날짜 변경 시 자동 리셋
    - 만료된 프리미엄은 자동으로 무료 전환
    """
    # 1. Subscription 조회
    subscription = await get_subscription_by_user_id(session, user_id)
    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="구독 정보를 찾을 수 없어요.",
        )
    
    # 2. 만료 체크 및 자동 처리
    await check_and_update_subscription_status(session, subscription)
    
    # 3. 날짜 체크 및 리셋
    today = date.today()
    if subscription.last_reset_date != today:
        subscription.daily_usage_count = 0
        subscription.last_reset_date = today
        await session.commit()
        await session.refresh(subscription)
    
    # 4. 프리미엄 분기
    if subscription.is_premium:
        return UsageResponse(
            is_premium=True,
            remaining_count=None,  # 무제한
            daily_limit=None,      # 무제한
            used_count=0,          # 카운트 안 함
        )
    
    # 5. 무료 사용자
    daily_limit = 5
    used_count = subscription.daily_usage_count
    remaining_count = max(0, daily_limit - used_count)
    
    return UsageResponse(
        is_premium=False,
        remaining_count=remaining_count,
        daily_limit=daily_limit,
        used_count=used_count,
    )