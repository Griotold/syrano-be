# app/routers/billing.py
from __future__ import annotations

import logging
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.services.subscriptions import (
    activate_subscription,
    get_subscription_by_user_id,
)

logger = logging.getLogger("syrano")
router = APIRouter()


class SubscribeRequest(BaseModel):
    user_id: str
    plan_type: Literal["weekly", "monthly"]


class SubscriptionStatusResponse(BaseModel):
    user_id: str
    is_premium: bool
    plan_type: str | None = None
    expires_at: datetime | None = None


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