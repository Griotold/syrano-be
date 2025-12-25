from __future__ import annotations

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.services.users import get_or_create_anonymous_user

from app.services.subscriptions import get_subscription_by_user_id

logger = logging.getLogger("syrano")

router = APIRouter()

class AnonymousAuthResponse(BaseModel):
    user_id: str
    is_premium: bool

class SubscriptionStatusResponse(BaseModel):
    user_id: str
    is_premium: bool
    plan_type: str | None = None
    expires_at: datetime | None = None


@router.post("/anonymous", response_model=AnonymousAuthResponse)
async def auth_anonymous(
    # ✅ body 파라미터 완전 제거
    session: AsyncSession = Depends(get_session),
):
    """
    새 익명 유저 생성 (항상 새로 생성)
    
    - body 없이 호출
    - 항상 새 User + 기본 Subscription 생성
    - 기존 사용자 확인은 GET /auth/me/subscription 사용
    """
    try:
        # ✅ user_id=None으로 고정 (항상 새 유저 생성)
        user = await get_or_create_anonymous_user(
            session=session,
            user_id=None,
        )
        
        # ✅ 새 유저는 항상 is_premium=False
        return AnonymousAuthResponse(
            user_id=user.id,
            is_premium=False,
        )
        
    except Exception as e:
        logger.exception("Failed to create anonymous user")
        raise HTTPException(
            status_code=500,
            detail="익명 유저 생성 중 오류가 발생했어요.",
        ) from e


@router.get("/me/subscription", response_model=SubscriptionStatusResponse)
async def get_my_subscription(
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    현재 유저의 구독 상태를 조회하는 엔드포인트.

    - Query string으로 user_id를 받는다.
    - 해당 user_id의 Subscription이 없으면 404를 반환한다.
    """
    subscription = await get_subscription_by_user_id(session, user_id)

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="구독 정보를 찾을 수 없어요.",
        )

    return SubscriptionStatusResponse(
        user_id=subscription.user_id,
        is_premium=subscription.is_premium,
        plan_type=subscription.plan_type,
        expires_at=subscription.expires_at,
    )