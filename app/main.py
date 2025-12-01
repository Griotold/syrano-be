from typing import List, Literal

from fastapi import FastAPI
from pydantic import BaseModel

from app.services.llm import generate_suggestions_from_conversation

app = FastAPI(title="Syrano API")


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
    is_premium: bool = False   # ⭐️ 추가

class GenerateResponse(BaseModel):
    suggestions: List[str]


@app.post("/rizz/generate", response_model=GenerateResponse)
async def generate_rizz(req: GenerateRequest):
    """
    이제는 LangChain + OpenAI LLM으로 실제 답장을 생성하는 버전.
    """
    suggestions = await generate_suggestions_from_conversation(
        conversation=req.conversation,
        platform=req.platform,
        relationship=req.relationship,
        style=req.style,
        tone=req.tone,
        num_suggestions=req.num_suggestions,
        is_premium=req.is_premium,
    )

    return GenerateResponse(suggestions=suggestions)