# TODO

## 🔴 High Priority (MVP 완성 전)

### 1. Anonymous Auth API 개선
**상태:** ✅ **완료**

**변경 사항:**
- `POST /auth/anonymous`: user_id 파라미터 제거, 항상 새 사용자 생성
- 기존 사용자 확인: `GET /auth/me/subscription?user_id=xxx` 사용

---

### 2. Profile CRUD API 구현
**상태:** ✅ **완료**

**구현 내용:**

#### 2.1 Profile 테이블 ✅
- User 1:N Profile 관계
- 필드: name, age, gender, memo
- MBTI 제외 (범용성 고려)

#### 2.2 API 엔드포인트 ✅
```
POST   /profiles              - 프로필 생성
GET    /profiles?user_id=xxx  - 사용자의 프로필 목록
GET    /profiles/{profile_id} - 특정 프로필 조회
PUT    /profiles/{profile_id} - 프로필 수정
DELETE /profiles/{profile_id} - 프로필 삭제
```

#### 2.3 analyze-image API 개선 🔴 **다음 작업**
```python
# 기존
POST /rizz/analyze-image
{
  "image": file,
  "user_id": "...",
  "platform": "kakao",      # 제거 예정
  "relationship": "...",     # 제거 예정
  "style": "banmal",         # 제거 예정
  "tone": "friendly",        # 제거 예정
  "num_suggestions": 3
}

# 개선 예정
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
**예상 시간:** 2시간

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
...

### 5. 무료 사용자 일일 제한
...

---

## 🟢 Low Priority (나중에)

### 6. 실제 결제 연동
...

### 7. OCR 이미지 전처리
...

### 8. 에러 핸들링 개선
...

### 9. CORS 프로덕션 설정
...

### 10. 로깅 개선
...

---

## 📊 Progress Tracker

- [x] Anonymous Auth API 개선 ✅
- [x] Profile CRUD 구현 ✅
- [ ] Profile 기반 analyze-image 개선 🔴 **다음 작업**
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
2. ✅ ~~Anonymous Auth 개선~~ (완료)
3. ✅ ~~Profile CRUD~~ (완료)
4. 🔴 **Profile 기반 analyze-image 개선** (2시간)
5. 🟡 Message History (2시간)

**총 예상 시간:** 4시간