from typing import List

from langchain_openai import ChatOpenAI

from app.config import (
    OPENAI_API_KEY,
    OPENAI_STANDARD_MODEL,
    OPENAI_PREMIUM_MODEL,
)


def get_llm(is_premium: bool = False) -> ChatOpenAI:
    """
    프리미엄 여부에 따라 사용할 모델을 선택.
    지금은 is_premium=False만 쓸 거고,
    나중에 구독 붙이면 True로도 호출할 거야.
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
    platform: str,
    relationship: str,
    style: str,
    tone: str,
    num_suggestions: int = 3,
    is_premium: bool = False,
) -> List[str]:
    """
    대화 캡처(텍스트)를 기반으로 답장 후보들을 생성하는 함수.
    FastAPI 엔드포인트에서 호출해줄 거야.
    """
    llm = get_llm(is_premium=is_premium)

    system_msg = (
        "너는 한국어 연애 메시지를 도와주는 AI 시라노(Syrano)야. "
        "사용자의 말투 설정(존댓말/반말, 톤)을 꼭 반영하고, "
        "짧고 자연스러운 메신저 스타일로 1~2문장만 생성해."
        "상대를 부담스럽게 하거나 과하게 공격적인/성적인 표현은 피하고,"
        "친근하지만 예의 있는 톤을 유지해."
    )

    # user 프롬프트는 그냥 f-string으로 간단히 구성
    user_msg = f"""
다음은 내가 상대와 나눈 대화야. (캡처에서 OCR로 뽑은 텍스트라고 생각하면 돼)

[플랫폼]
{platform}

[관계]
{relationship}

[말투]
{style}

[톤]
{tone}

[대화 내용]
{conversation}

위 대화를 바탕으로, 내가 보낼 수 있는 답장을 {num_suggestions}개 추천해줘.

조건:
- 각 답장은 1~2문장 정도의 짧은 카카오톡/DM 스타일로 만들어줘.
- 각 답장은 줄바꿈으로만 구분하고, 번호(1., 2. 같은 것)는 붙이지 마.
- 말투, 톤, 관계 설정을 최대한 반영해줘.
"""

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]

    # LangChain의 ChatOpenAI는 messages 리스트를 그대로 받을 수 있음
    response = await llm.ainvoke(messages)

    # "한 줄 = 한 문장" 식으로 분리 (프롬프트에서 그렇게 요청했으니까)
    lines = [line.strip() for line in response.content.split("\n") if line.strip()]

    # 요청한 개수만큼 자르기
    return lines[:num_suggestions]