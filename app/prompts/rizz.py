from app.models.profile import Profile


def build_system_prompt() -> str:
    """
    Rizz 시스템 프롬프트
    """
    return (
        "You are Syrano, an AI assistant that helps users with dating messages in Korean and English. "
        "Based on the conversation partner's information (name, age, gender, memo) and chat context, "
        "generate 1-2 sentence replies in a natural messenger style. "
        "Match the language of the conversation (Korean or English). "
        "Avoid being overly aggressive or making the other person uncomfortable. "
        "Keep a friendly, warm, and appropriate tone for the relationship context."
    )


def build_user_prompt(
    conversation: str,
    profile: Profile,
    num_suggestions: int = 3,
) -> str:
    """
    사용자 프롬프트 (Profile 기반)
    """
    # None 처리
    age_str = f"{profile.age}세" if profile.age else "알 수 없음"
    gender_str = profile.gender or "알 수 없음"
    memo_str = profile.memo or "없음"
    
    profile_info = f"""
상대방 정보:
- 이름: {profile.name}
- 나이: {age_str}
- 성별: {gender_str}
- 메모: {memo_str}
""".strip()

    return f"""
{profile_info}

대화 내용 (OCR로 추출됨, 오타 있을 수 있음):
{conversation}

위 대화를 분석하고, 다음 조건에 맞는 답장을 {num_suggestions}개 추천해줘:

1. 대화 언어 파악 (한국어/영어) 후 같은 언어로 답장
2. 상대방의 말투 분석 (존댓말/반말, casual/formal)
3. 대화 분위기 고려 (친근한지, 로맨틱한지, 가벼운지 등)
4. 상대방 정보(나이, 성별, 메모)를 자연스럽게 반영
5. 각 답장은 1~2문장의 짧은 메신저 스타일
6. **대화가 자연스럽게 이어질 수 있도록 질문이나 화제 제시 포함** ✅ 추가
7. 각 답장은 줄바꿈으로만 구분, 번호 없이
8. 상대를 불편하게 하거나 지나치게 공격적이지 않게
9. 대화 맥락상 자연스럽다면 살짝 로맨틱하거나 장난스러운 표현도 OK
"""