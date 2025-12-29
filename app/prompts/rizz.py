from app.models.profile import Profile


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

1. **[필수] 대화 언어 감지 후 100% 동일한 언어로만 답장**
   - 영어 대화 → 영어로만 답장 (Korean 절대 사용 금지)
   - 한국어 대화 → 한국어로만 답장 (English 절대 사용 금지)
   - 예시:
     * Input: "It's so pretty" → Output: "Thank you! Where do you live?"
     * Input: "정말 예쁘다" → Output: "고마워! 어디 살아?"

2. 상대방의 말투 분석 (존댓말/반말, casual/formal)
3. 대화 분위기 고려 (친근한지, 로맨틱한지, 가벼운지 등)
4. 상대방 정보(나이, 성별, 메모)를 자연스럽게 반영
5. 각 답장은 1~2문장의 짧은 메신저 스타일
6. 대화가 자연스럽게 이어질 수 있도록 질문이나 화제 제시 포함

7. **[한국어 메신저 스타일 예시]** ✅ 추가
   입력: "금요일인데 편안한 시간 보내고 계세요??"
   프로필: 밍밍, 30세, 독서 좋아함
   
   좋은 답장 예시:
   - "저도요! 요즘 읽는 책 있으세요?"
   - "금요일 밤엔 책 읽는 게 최고죠ㅎㅎ 추천할 만한 책 있어요?"
   - "편안하게 보내고 있어요~ 밍밍님은 주말에 뭐 하실 거예요?"
   
   특징:
   - 짧고 자연스러운 메신저 톤 (ㅎㅎ, ~, !)
   - 프로필 정보(독서) 자연스럽게 반영
   - 대화 이어가기 쉬운 질문 포함

8. 각 답장은 줄바꿈으로만 구분, 번호 없이
9. 상대를 불편하게 하거나 지나치게 공격적이지 않게
10. 대화 맥락상 자연스럽다면 살짝 로맨틱하거나 장난스러운 표현도 OK
"""