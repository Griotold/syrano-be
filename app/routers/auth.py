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


class AnonymousAuthRequest(BaseModel):
    user_id: Optional[str] = None
    # 나중에 디바이스 정보 등 붙이고 싶으면 여기에 확장 가능


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
    body: AnonymousAuthRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    익명 유저 발급/조회용 엔드포인트.

    - body.user_id가 없으면: 새 User + 기본 Subscription 생성 후 user_id 반환
    - body.user_id가 있으면: 해당 User가 있으면 재사용, 없으면 새로 생성
    """
    try:
        user = await get_or_create_anonymous_user(
            session=session,
            user_id=body.user_id,
        )
    except Exception as e:
        logger.exception("Failed to create/get anonymous user")
        raise HTTPException(
            status_code=500,
            detail="익명 유저 생성 중 오류가 발생했어요.",
        ) from e

    # Subscription에서 is_premium 상태를 확인하는 로직은
    # 나중에 확장할 예정이지만, 지금은 기본 False로 내려도 충분함.
    # (혹은 필요하면 Subscription 조회 쿼리를 추가해도 됨)
    return AnonymousAuthResponse(
        user_id=user.id,
        is_premium=False,
    )

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
        # 유저가 없거나, 구독이 아직 생성되지 않은 경우
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