from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.db import get_session
from app.schemas.billing import (
    SubscribeRequest,
    VerifyReceiptRequest,
    SubscriptionStatusResponse,
    UsageResponse,
)
from app.services.subscriptions import (
    activate_subscription,
    get_subscription_by_user_id,
    check_and_update_subscription_status,
)
from app.services.receipt_verification import (
    verify_apple_receipt,
    verify_google_receipt,
    find_subscription_by_transaction_id,
    transfer_subscription_to_new_user,
)

from typing import Any
import jwt
from jwt import PyJWKClient

from app.services.webhook_handlers import (
    handle_renewal,
    handle_renewal_failure,
    handle_expiration,
    handle_refund,
)

logger = logging.getLogger("syrano")
router = APIRouter()


@router.post("/subscribe", response_model=SubscriptionStatusResponse)
async def subscribe(
    body: SubscribeRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    프리미엄 구독 활성화 (테스트/관리자용)
    
    ⚠️ 실제 결제 없음! 테스트 및 관리자 수동 활성화용
    ⚠️ 프로덕션에서는 /verify-receipt 사용
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


@router.post("/verify-receipt", response_model=SubscriptionStatusResponse)
async def verify_receipt(
    body: VerifyReceiptRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Apple/Google 영수증 검증 및 프리미엄 활성화
    
    - iOS: Apple App Store 영수증 검증
    - Android: Google Play 영수증 검증
    - transaction_id 기반 중복 방지
    - 구독 복원 지원 (앱 재설치 시)
    """
    try:
        # 1. 플랫폼별 영수증 검증
        if body.platform == "ios":
            verified_data = await verify_apple_receipt(body.receipt_data)
        else:
            verified_data = await verify_google_receipt(body.receipt_data)
        
        # 2. transaction_id로 기존 구독 찾기
        existing_subscription = await find_subscription_by_transaction_id(
            session, 
            verified_data["transaction_id"]
        )
        
        if existing_subscription:
            # 3-A. 기존 구독 발견 → 복원 (user_id 변경)
            logger.info(
                f"Restoring subscription {verified_data['transaction_id']}: "
                f"{existing_subscription.user_id} → {body.user_id}"
            )
            await transfer_subscription_to_new_user(
                session,
                old_user_id=existing_subscription.user_id,
                new_user_id=body.user_id,
            )
            subscription = await get_subscription_by_user_id(session, body.user_id)
        else:
            # 3-B. 새 구독 생성
            subscription = await activate_subscription(
                session=session,
                user_id=body.user_id,
                plan_type=verified_data["plan_type"],
                transaction_id=verified_data["transaction_id"],
                platform=body.platform,
                original_transaction_id=verified_data.get("original_transaction_id"),
            )
        
        return SubscriptionStatusResponse(
            user_id=subscription.user_id,
            is_premium=subscription.is_premium,
            plan_type=subscription.plan_type,
            expires_at=subscription.expires_at,
        )
        
    except ValueError as e:
        # 영수증 검증 실패
        raise HTTPException(status_code=400, detail=str(e)) from e
    except httpx.HTTPError as e:
        # Apple/Google API 통신 오류
        logger.exception("Receipt verification HTTP error")
        raise HTTPException(
            status_code=502,
            detail="영수증 검증 서버와 통신 중 오류가 발생했습니다.",
        ) from e
    except Exception:
        # 기타 오류
        logger.exception("Failed to verify receipt")
        raise HTTPException(
            status_code=500,
            detail="영수증 검증 중 오류가 발생했습니다.",
        )


@router.get("/usage", response_model=UsageResponse)
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
    from datetime import date
    
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
            remaining_count=None,
            daily_limit=None,
            used_count=0,
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

@router.post("/webhook/apple")
async def apple_webhook(
    body: dict[str, Any],
    session: AsyncSession = Depends(get_session),
):
    """
    Apple App Store Server Notifications (Version 2)
    
    자동 갱신/취소/환불 이벤트 수신
    
    Apple이 자동으로 호출하는 엔드포인트
    - 자동 갱신 성공/실패
    - 구독 취소
    - 환불
    - 만료
    """
    try:
        # 1. JWT 검증 (Apple이 보낸 게 맞는지)
        signed_payload = body.get("signedPayload")
        if not signed_payload:
            logger.warning("Apple webhook: Missing signedPayload")
            return {"status": "error", "message": "Missing signedPayload"}
        
        # 2. Apple Public Key로 JWT 검증
        decoded = _verify_apple_webhook_jwt(signed_payload)
        
        # 3. 이벤트 타입 확인
        notification_type = decoded.get("notificationType")
        data = decoded.get("data", {})
        transaction_info = data.get("transactionInfo", {})
        transaction_id = transaction_info.get("transactionId")
        
        if not transaction_id:
            logger.warning(f"Apple webhook: Missing transactionId in {notification_type}")
            return {"status": "error", "message": "Missing transactionId"}
        
        logger.info(f"Apple webhook: {notification_type} for {transaction_id}")
        
        # 4. 이벤트별 처리
        if notification_type == "DID_RENEW":
            # 자동 갱신 성공
            await handle_renewal(session, transaction_id, transaction_info)
        
        elif notification_type == "DID_FAIL_TO_RENEW":
            # 갱신 실패
            await handle_renewal_failure(session, transaction_id)
        
        elif notification_type == "DID_CHANGE_RENEWAL_STATUS":
            # 사용자가 자동갱신 껐다 켰다
            subtype = decoded.get("subtype")
            logger.info(f"Renewal status changed: {subtype} for {transaction_id}")
        
        elif notification_type == "EXPIRED":
            # 만료됨
            await handle_expiration(session, transaction_id)
        
        elif notification_type == "REFUND":
            # 환불됨
            await handle_refund(session, transaction_id)
        
        else:
            logger.info(f"Unhandled Apple webhook event: {notification_type}")
        
        return {"status": "ok"}
        
    except jwt.InvalidTokenError as e:
        logger.error(f"Apple webhook JWT verification failed: {e}")
        return {"status": "error", "message": "Invalid JWT"}
    
    except Exception as e:
        logger.exception("Apple webhook processing failed")
        # Webhook은 항상 200 OK 반환해야 재전송 안 함
        return {"status": "error", "message": str(e)}


def _verify_apple_webhook_jwt(signed_payload: str) -> dict:
    """
    Apple JWT 검증
    
    Apple Public Key로 서명 검증
    Public Key URL: https://appleid.apple.com/auth/keys
    
    Args:
        signed_payload: Apple이 보낸 JWT 토큰
        
    Returns:
        검증된 JWT payload
        
    Raises:
        jwt.InvalidTokenError: 잘못된 JWT
    """
    try:
        # Apple Public Key 가져오기 (자동 캐싱)
        jwks_client = PyJWKClient("https://appleid.apple.com/auth/keys")
        
        # JWT Header에서 kid 추출 후 매칭되는 Public Key 가져오기
        signing_key = jwks_client.get_signing_key_from_jwt(signed_payload)
        
        # JWT 검증 및 디코딩
        decoded = jwt.decode(
            signed_payload,
            signing_key.key,
            algorithms=["ES256"],
            options={"verify_exp": True},
        )
        
        return decoded
        
    except jwt.InvalidTokenError:
        raise
    except Exception as e:
        logger.exception("Apple webhook JWT verification error")
        raise jwt.InvalidTokenError(f"JWT verification failed: {e}")