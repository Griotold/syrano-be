from __future__ import annotations

import logging
from typing import List, Literal

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.services.llm import generate_suggestions_from_conversation
from app.services.subscriptions import get_subscription_by_user_id

logger = logging.getLogger("syrano")
router = APIRouter()


class GenerateRequest(BaseModel):
    mode: Literal["conversation"] = "conversation"
    conversation: str
    platform: str = "kakao"
    relationship: str = "first_meet"
    style: str = "banmal"
    tone: str = "friendly"
    num_suggestions: int = 3
    is_premium: bool = False
    user_id: str  # 이제 필수


class GenerateResponse(BaseModel):
    suggestions: List[str]


@router.post("/generate", response_model=GenerateResponse)
async def generate_rizz(
    req: GenerateRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Rizz 메시지 생성 엔드포인트.
    - user_id를 기반으로 DB에서 구독 상태를 조회해서 is_premium을 결정한다.
    """

    # 1) user_id로 구독 조회
    subscription = await get_subscription_by_user_id(session, req.user_id)
    if subscription is None:
        # 유효하지 않은 user_id → 클라이언트가 /auth/anonymous 안 거쳤을 가능성
        raise HTTPException(
            status_code=404,
            detail="해당 user_id의 구독 정보를 찾을 수 없어요. 다시 로그인(익명 인증)해 주세요.",
        )

    is_premium = subscription.is_premium

    logger.info(
        "Generate rizz called",
        extra={
            "platform": req.platform,
            "relationship": req.relationship,
            "style": req.style,
            "tone": req.tone,
            "num_suggestions": req.num_suggestions,
            "user_id": req.user_id,
            "is_premium": is_premium,
        },
    )

    try:
        suggestions = await generate_suggestions_from_conversation(
            conversation=req.conversation,
            platform=req.platform,
            relationship=req.relationship,
            style=req.style,
            tone=req.tone,
            num_suggestions=req.num_suggestions,
            is_premium=is_premium,  # ⭐️ 이제 DB 기반
        )
    except Exception as e:
        logger.exception("Error while generating suggestions from LLM")
        raise HTTPException(
            status_code=500,
            detail="메시지 생성 중 오류가 발생했어요. 잠시 후 다시 시도해주세요.",
        ) from e

    if not suggestions:
        logger.error("LLM returned empty suggestions")
        raise HTTPException(
            status_code=500,
            detail="메시지를 생성하지 못했어요. 다시 한 번 시도해볼래요?",
        )

    return GenerateResponse(suggestions=suggestions)