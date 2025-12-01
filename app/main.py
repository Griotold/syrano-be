import logging
from typing import List, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.services.llm import generate_suggestions_from_conversation

app = FastAPI(title="Syrano API")

logger = logging.getLogger("syrano")
logging.basicConfig(level=logging.INFO)

@app.get("/health")
def health_check():
    return {"status": "ok"}


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


@app.post("/rizz/generate", response_model=GenerateResponse)
async def generate_rizz(req: GenerateRequest):
    """
    LangChain + OpenAI LLM으로 실제 답장을 생성하는 엔드포인트.
    간단한 로깅과 에러 처리를 추가했다.
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
        # 사용자에게 너무 상세한 내용은 노출 안 하고, 메시지만 간단히 줌
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