from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class SubscribeRequest(BaseModel):
    """프리미엄 구독 요청"""
    user_id: str
    plan_type: Literal["weekly", "monthly"]


class VerifyReceiptRequest(BaseModel):
    """영수증 검증 요청"""
    user_id: str
    receipt_data: str  # Base64 encoded receipt
    platform: Literal["ios", "android"]


class SubscriptionStatusResponse(BaseModel):
    """구독 상태 응답"""
    user_id: str
    is_premium: bool
    plan_type: str | None = None
    expires_at: datetime | None = None


class UsageResponse(BaseModel):
    """사용량 조회 응답"""
    is_premium: bool
    remaining_count: int | None  # None: 무제한
    daily_limit: int | None      # None: 무제한
    used_count: int