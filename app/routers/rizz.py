from __future__ import annotations

import logging
from typing import List, Literal

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.services.llm import generate_suggestions_from_conversation

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
    user_id: str | None = None


class GenerateResponse(BaseModel):
    suggestions: List[str]


@router.post("/generate", response_model=GenerateResponse)
async def generate_rizz(
    req: GenerateRequest,
    session: AsyncSession = Depends(get_session),  # 지금은 안 써도, 나중에 user_id/구독/히스토리용
):
    """
    LangChain + OpenAI LLM으로 실제 답장을 생성하는 엔드포인트.
    간단한 로깅과 에러 처리를 포함한다.
    """
    logger.info(
        "Generate rizz called",
        extra={
            "platform": req.platform,
            "relationship": req.relationship,
            "style": req.style,
            "tone": req.tone,
            "num_suggestions": req.num_suggestions,
            "is_premium": req.is_premium,
            "has_user_id": req.user_id is not None,
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
            is_premium=req.is_premium,
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