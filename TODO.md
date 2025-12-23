# TODO

## 🔴 High Priority (MVP 완성 전)

### 1. Anonymous Auth API 개선
**문제:**
- `POST /auth/anonymous`가 `user_id`를 입력받고 다시 리턴하는 구조가 혼란스러움
- "익명 인증"인데 ID를 미리 알아야 함

**개선안:**
```
Option 1: user_id 입력 제거
- 요청: {} (빈 body)
- 응답: { "user_id": "새로생성된ID", "is_premium": false }
- 기존 사용자 확인은 GET /auth/me/subscription으로

Option 2: 분리
- POST /auth/anonymous (새 사용자 생성)
- POST /auth/login (기존 user_id로 로그인)
```

**우선순위:** High  
**예상 시간:** 1시간

---

### 2. Profile CRUD API 구현
**현재 상황:**
- `/rizz/analyze-image`가 `platform`, `relationship`, `style`, `tone`을 매번 받음
- Flutter 프로필 화면(이름, 나이, MBTI, 성별, 메모)과 불일치

**구현 내용:**

#### 2.1 Profile 테이블
```sql
CREATE TABLE profiles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    mbti VARCHAR(4),
    gender VARCHAR(10),
    memo TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
```

#### 2.2 API 엔드포인트
```
POST   /profiles              - 프로필 생성
GET    /profiles?user_id=xxx  - 사용자의 프로필 목록
GET    /profiles/{profile_id} - 특정 프로필 조회
PUT    /profiles/{profile_id} - 프로필 수정
DELETE /profiles/{profile_id} - 프로필 삭제
```

#### 2.3 analyze-image API 개선
```python
# 기존
POST /rizz/analyze-image
{
  "image": file,
  "user_id": "...",
  "platform": "kakao",      # 제거
  "relationship": "...",     # 제거
  "style": "banmal",         # 제거
  "tone": "friendly",        # 제거
  "num_suggestions": 3
}

# 개선
POST /rizz/analyze-image
{
  "image": file,
  "user_id": "...",
  "profile_id": "...",       # 추가
  "num_suggestions": 3
}

# 백엔드에서 profile_id로 프로필 조회 후 프롬프트에 활용
```

**우선순위:** High  
**예상 시간:** 3시간

---

## 🟡 Medium Priority (MVP 이후)

### 3. OCR 프롬프트 최적화
**현재:**
- OCR 추출 텍스트를 그대로 LLM에 전달
- 프로필 정보 미활용

**개선:**
```python
user_prompt = f"""
상대방 정보:
- 이름: {profile.name}
- 나이: {profile.age}세
- MBTI: {profile.mbti}
- 성별: {profile.gender}
- 메모: {profile.memo}

채팅 대화 내용 (OCR 추출, 오타 가능):
{conversation}

위 맥락을 고려하여:
1. 상대방의 말투 분석 (존댓말/반말)
2. 대화 분위기 파악
3. 자연스러운 답장 {num_suggestions}개 추천
"""
```

**우선순위:** Medium  
**예상 시간:** 2시간

---

### 4. Message History 저장
**현재:**
- `message_history` 테이블은 있지만 데이터 저장 안 함

**구현:**
```python
# /rizz/generate, /rizz/analyze-image 완료 후
await session.execute(
    insert(MessageHistory).values(
        user_id=user_id,
        conversation=conversation,
        suggestions={"items": suggestions}
    )
)
```

**활용:**
- 사용자별 사용 통계
- 무료 사용자 일일 제한 (예: 10회/일)
- 히스토리 조회 기능

**우선순위:** Medium  
**예상 시간:** 2시간

---

### 5. 무료 사용자 일일 제한
**구현:**
```python
# /rizz/generate, /rizz/analyze-image 시작 부분
if not is_premium:
    today_count = await get_today_message_count(session, user_id)
    if today_count >= FREE_DAILY_LIMIT:  # 예: 10
        raise HTTPException(
            status_code=429,
            detail="무료 사용 횟수를 초과했어요. 프리미엄으로 업그레이드하세요!"
        )
```

**우선순위:** Medium  
**예상 시간:** 1시간

---

## 🟢 Low Priority (나중에)

### 6. 실제 결제 연동
**현재:**
- `POST /billing/subscribe`가 단순 DB 업데이트

**구현:**
- iOS: App Store receipt validation
- Android: Google Play billing verification
- 영수증 검증 → DB 업데이트

**우선순위:** Low  
**예상 시간:** 1주일

---

### 7. OCR 이미지 전처리
**목적:** OCR 정확도 향상

**구현:**
```python
from PIL import Image, ImageEnhance

def preprocess_image(image_path):
    img = Image.open(image_path)
    # 선명도 증가
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)
    # 대비 증가
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    return img
```

**우선순위:** Low  
**예상 시간:** 2시간

---

### 8. 에러 핸들링 개선
**현재:**
- 일부 에러가 500으로 처리됨

**개선:**
- Custom Exception 클래스
- 에러 코드 체계화
- 사용자 친화적 메시지

**우선순위:** Low  
**예상 시간:** 3시간

---

### 9. CORS 프로덕션 설정
**현재:**
```python
allow_origins=["*"]  # 모든 origin 허용
```

**개선:**
```python
allow_origins=[
    "https://syrano.app",
    "https://www.syrano.app"
]
```

**우선순위:** Low (네이티브 앱은 CORS 무관)  
**예상 시간:** 10분

---

### 10. 로깅 개선
**현재:**
- 기본 로깅만 사용

**개선:**
- 구조화된 로깅 (JSON)
- 요청/응답 추적 ID
- 에러 스택 트레이스 수집
- Sentry 연동

**우선순위:** Low  
**예상 시간:** 4시간

---

## 📊 Progress Tracker

- [ ] Anonymous Auth API 개선
- [ ] Profile CRUD 구현
- [ ] Profile 기반 OCR 프롬프트
- [ ] Message History 저장
- [ ] 무료 사용자 일일 제한
- [ ] 실제 결제 연동
- [ ] OCR 이미지 전처리
- [ ] 에러 핸들링 개선
- [ ] CORS 프로덕션 설정
- [ ] 로깅 개선

---

## 🎯 Next Sprint (우선 작업)

1. ✅ ~~OCR 통합~~ (완료)
2. 🔴 Anonymous Auth 개선 (1시간)
3. 🔴 Profile CRUD (3시간)
4. 🟡 Message History (2시간)

**총 예상 시간:** 6시간