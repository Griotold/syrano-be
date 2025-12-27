from typing import List

from langchain_openai import ChatOpenAI

from app.config import (
    OPENAI_API_KEY,
    OPENAI_STANDARD_MODEL,
    OPENAI_PREMIUM_MODEL,
)
from app.models.profile import Profile
from app.prompts.rizz import build_system_prompt, build_user_prompt


def get_llm(is_premium: bool = False) -> ChatOpenAI:
    """
    프리미엄 여부에 따라 사용할 모델을 선택.
    """
    model_name = OPENAI_PREMIUM_MODEL if is_premium else OPENAI_STANDARD_MODEL

    return ChatOpenAI(
        model=model_name,
        temperature=0.8,
        api_key=OPENAI_API_KEY,
    )


async def generate_suggestions_from_conversation(
    *,
    conversation: str,
    profile: Profile,
    num_suggestions: int = 3,
    is_premium: bool = False,
) -> List[str]:
    """
    대화 캡처(텍스트) + 상대방 프로필 정보를 기반으로 답장 후보들을 생성.
    """
    llm = get_llm(is_premium=is_premium)
    
    # 프롬프트는 prompts 모듈에서 가져옴
    system_msg = build_system_prompt()
    user_msg = build_user_prompt(
        conversation=conversation,
        profile=profile,
        num_suggestions=num_suggestions,
    )
    
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]

    response = await llm.ainvoke(messages)

    # 줄바꿈으로 분리
    lines = [line.strip() for line in response.content.split("\n") if line.strip()]

    # 요청한 개수만큼 자르기
    return lines[:num_suggestions]