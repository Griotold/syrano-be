from typing import List, Literal

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Syrano API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


class GenerateRequest(BaseModel):
    mode: Literal["conversation"] = "conversation"  # 일단 대화 캡처 모드만
    conversation: str                               # OCR로 뽑힌 전체 대화
    platform: str = "kakao"                         # kakao / instagram ...
    relationship: str = "first_meet"                # first_meet / some / couple ...
    style: str = "banmal"                           # banmal / honorific
    tone: str = "friendly"                          # friendly / serious / funny ...
    num_suggestions: int = 3                        # 몇 개 뽑을지


class GenerateResponse(BaseModel):
    suggestions: List[str]


@app.post("/rizz/generate", response_model=GenerateResponse)
async def generate_rizz(req: GenerateRequest):
    """
    아직은 LLM 없이 mock 응답만 돌려주는 버전.
    나중에 여기만 LLM 호출로 교체하면 됨.
    """
    # 관계에 따라 기본 문장 다르게
    if req.relationship == "first_meet":
        base = "어제 얘기 너무 즐거웠어요 ㅎㅎ"
    else:
        base = "요즘 바쁜데도 연락해줘서 고마워 :)"

    # 말투/톤에 따라 살짝 변형 (장난스러운 mock 로직)
    if req.style == "honorific":
        base = base.replace("ㅎㅎ", "") + " 잘 지내고 계시죠?"
    else:
        base = base + " 오늘 하루는 어땠어?"

    suggestions = [
        base,
        base.replace("오늘 하루는 어땠어?", "이번 주에 시간 되면 또 보자!"),
        base.replace("오늘 하루는 어땠어?", "다음에 커피 한 잔 하자 ☕️"),
    ]

    return GenerateResponse(suggestions=suggestions[: req.num_suggestions])