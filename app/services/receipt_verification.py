from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TypedDict

import httpx
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Subscription, Profile, User

from app.config import APPLE_SHARED_SECRET

logger = logging.getLogger("syrano")


class VerifiedReceiptData(TypedDict):
    """검증된 영수증 데이터"""
    transaction_id: str
    original_transaction_id: str | None
    plan_type: str
    expires_at: datetime


async def verify_apple_receipt(receipt_data: str) -> VerifiedReceiptData:
    """
    Apple App Store 영수증 검증
    
    Args:
        receipt_data: Base64 인코딩된 영수증
        
    Returns:
        VerifiedReceiptData: 검증된 영수증 정보
        
    Raises:
        ValueError: 잘못된 영수증
        httpx.HTTPError: 네트워크 오류
    """
    # Apple 검증 URL (프로덕션)
    # 테스트: https://sandbox.itunes.apple.com/verifyReceipt
    url = "https://buy.itunes.apple.com/verifyReceipt"
    
    # TODO: 환경변수로 이동
    # APPLE_SHARED_SECRET=your_shared_secret
    shared_secret = APPLE_SHARED_SECRET

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={
                "receipt-data": receipt_data,
                "password": shared_secret,
                "exclude-old-transactions": True,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
    
    # 응답 상태 확인
    status = data.get("status")
    if status != 0:
        raise ValueError(f"Invalid Apple receipt: status={status}")
    
    # 최신 영수증 정보 추출
    latest_receipt_info = data.get("latest_receipt_info")
    if not latest_receipt_info:
        raise ValueError("No receipt info found in Apple response")
    
    receipt = latest_receipt_info[0]
    
    # 필수 필드 추출
    transaction_id = receipt.get("transaction_id")
    original_transaction_id = receipt.get("original_transaction_id")
    product_id = receipt.get("product_id")
    expires_date_ms = receipt.get("expires_date_ms")
    
    if not all([transaction_id, product_id, expires_date_ms]):
        raise ValueError("Incomplete receipt data from Apple")
    
    # product_id로 plan_type 결정
    if "weekly" in product_id.lower():
        plan_type = "weekly"
    elif "monthly" in product_id.lower():
        plan_type = "monthly"
    else:
        raise ValueError(f"Unknown product_id: {product_id}")
    
    # expires_at 변환
    expires_at = datetime.fromtimestamp(
        int(expires_date_ms) / 1000, 
        tz=timezone.utc
    )
    
    return VerifiedReceiptData(
        transaction_id=transaction_id,
        original_transaction_id=original_transaction_id,
        plan_type=plan_type,
        expires_at=expires_at,
    )


async def verify_google_receipt(receipt_data: str) -> VerifiedReceiptData:
    """
    Google Play 영수증 검증
    
    TODO: Google Play Developer API 연동
    - Service Account 생성
    - API 키 발급
    - 환경변수 설정
    """
    raise NotImplementedError(
        "Google Play receipt verification not implemented yet. "
        "Please use iOS for now."
    )


async def find_subscription_by_transaction_id(
    session: AsyncSession,
    transaction_id: str,
) -> Subscription | None:
    """
    transaction_id로 기존 구독 찾기
    
    Args:
        session: DB 세션
        transaction_id: Apple/Google 거래 ID
        
    Returns:
        기존 구독 또는 None
    """
    result = await session.execute(
        select(Subscription).where(Subscription.transaction_id == transaction_id)
    )
    return result.scalar_one_or_none()


async def transfer_subscription_to_new_user(
    session: AsyncSession,
    old_user_id: str,
    new_user_id: str,
) -> None:
    """
    구독을 old_user_id에서 new_user_id로 이전
    
    앱 재설치 후 구독 복원 시 사용
    
    Steps:
        1. subscriptions.user_id 변경
        2. profiles.user_id 변경
        3. old_user 삭제
        
    Args:
        session: DB 세션
        old_user_id: 기존 user_id
        new_user_id: 새 user_id
    """
    # 1. subscriptions 이전
    await session.execute(
        update(Subscription)
        .where(Subscription.user_id == old_user_id)
        .values(user_id=new_user_id)
    )
    
    # 2. profiles 이전
    await session.execute(
        update(Profile)
        .where(Profile.user_id == old_user_id)
        .values(user_id=new_user_id)
    )
    
    # 3. old_user 삭제
    await session.execute(
        delete(User).where(User.id == old_user_id)
    )
    
    await session.commit()
    
    logger.info(
        f"Transferred subscription from {old_user_id} to {new_user_id}"
    )