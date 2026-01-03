from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.receipt_verification import find_subscription_by_transaction_id

logger = logging.getLogger("syrano")


async def handle_renewal(
    session: AsyncSession,
    transaction_id: str,
    transaction_info: dict,
) -> None:
    """
    자동 갱신 성공 처리
    
    Args:
        session: DB 세션
        transaction_id: Apple/Google 거래 ID
        transaction_info: 영수증 정보
    """
    subscription = await find_subscription_by_transaction_id(
        session, 
        transaction_id
    )
    
    if not subscription:
        logger.warning(f"Subscription not found for renewal: {transaction_id}")
        return
    
    # expires_at 업데이트
    expires_ms = transaction_info.get("expiresDate")
    if expires_ms:
        expires_at = datetime.fromtimestamp(
            int(expires_ms) / 1000, 
            tz=timezone.utc
        )
        subscription.expires_at = expires_at
        subscription.is_premium = True  # 갱신 성공 시 프리미엄 유지
        await session.commit()
        logger.info(f"Renewed subscription: {transaction_id} → {expires_at}")


async def handle_renewal_failure(
    session: AsyncSession,
    transaction_id: str,
) -> None:
    """
    자동 갱신 실패 처리
    
    Args:
        session: DB 세션
        transaction_id: Apple/Google 거래 ID
    """
    subscription = await find_subscription_by_transaction_id(
        session, 
        transaction_id
    )
    
    if not subscription:
        logger.warning(f"Subscription not found for renewal failure: {transaction_id}")
        return
    
    # 유예 기간 없이 바로 무료 전환
    # TODO: 7일 유예 기간 추가 고려
    subscription.is_premium = False
    await session.commit()
    logger.warning(f"Renewal failed, subscription downgraded: {transaction_id}")


async def handle_expiration(
    session: AsyncSession,
    transaction_id: str,
) -> None:
    """
    구독 만료 처리
    
    Args:
        session: DB 세션
        transaction_id: Apple/Google 거래 ID
    """
    subscription = await find_subscription_by_transaction_id(
        session, 
        transaction_id
    )
    
    if not subscription:
        logger.warning(f"Subscription not found for expiration: {transaction_id}")
        return
    
    subscription.is_premium = False
    await session.commit()
    logger.info(f"Subscription expired: {transaction_id}")


async def handle_refund(
    session: AsyncSession,
    transaction_id: str,
) -> None:
    """
    환불 처리
    
    Args:
        session: DB 세션
        transaction_id: Apple/Google 거래 ID
    """
    subscription = await find_subscription_by_transaction_id(
        session, 
        transaction_id
    )
    
    if not subscription:
        logger.warning(f"Subscription not found for refund: {transaction_id}")
        return
    
    subscription.is_premium = False
    await session.commit()
    logger.warning(f"Subscription refunded and downgraded: {transaction_id}")