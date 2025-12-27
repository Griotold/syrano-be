# TODO

## 🔴 High Priority (MVP 완성 전)

### 1. Anonymous Auth API 개선
**상태:** ✅ **완료**

---

### 2. Profile CRUD API 구현
**상태:** ✅ **완료**

#### 2.1 Profile 테이블 ✅
#### 2.2 API 엔드포인트 ✅
#### 2.3 analyze-image API 개선 ✅ **완료**

**완료 내용:**
- `profile_id` 기반으로 프로필 정보 조회
- Profile 정보를 LLM 프롬프트에 반영
- 프롬프트 분리 (`app/prompts/rizz.py`)
- 대화 이어가기 개선 (질문/화제 제시 포함)

---

### 3. 프롬프트 최적화 ✅ **완료**

**완료 내용:**
- 프롬프트 분리: `app/prompts/rizz.py`
- Profile 정보 활용 (이름, 나이, 성별, 메모)
- 한국어/영어 자동 감지
- 대화 연속성 개선 (질문/화제 포함)
- 말투 유연성 개선 (로맨틱, 장난스러운 표현 허용)

---

## 🟡 Medium Priority (MVP 이후)

### 4. Message History 저장
**상태:** ⏸️ 대기

**내용:**
- `/rizz/analyze-image` 결과를 `message_history` 테이블에 저장
- 사용량 추적
- 무료 사용자 일일 제한 기반 마련

**예상 시간:** 2시간

---

### 5. 무료 사용자 일일 제한
**상태:** ⏸️ 대기

**내용:**
- Message History 기반으로 일일 사용량 체크
- 무료: 5회/일
- 프리미엄: 무제한

**예상 시간:** 2시간

---

## 🟢 Low Priority (나중에)

### 6. 실제 결제 연동
- App Store / Google Play 영수증 검증
- Subscription 만료 체크 자동화

### 7. OCR 이미지 전처리
- 저화질 이미지 개선
- 텍스트 영역 자동 크롭

### 8. 프롬프트 A/B 테스트
- 다양한 프롬프트 버전 테스트
- 사용자 피드백 수집

### 9. CORS 프로덕션 설정
- `allow_origins` 실제 도메인으로 제한

### 10. 로깅 개선
- 구조화된 로깅
- 에러 추적 강화

---

## 📊 Progress Tracker

- [x] Anonymous Auth API 개선 ✅
- [x] Profile CRUD 구현 ✅
- [x] Profile 기반 analyze-image 개선 ✅
- [x] 프롬프트 분리 및 최적화 ✅
- [ ] Message History 저장 ⏸️
- [ ] 무료 사용자 일일 제한 ⏸️
- [ ] 실제 결제 연동
- [ ] OCR 이미지 전처리
- [ ] 프롬프트 A/B 테스트
- [ ] CORS 프로덕션 설정
- [ ] 로깅 개선

---

## 🎯 Next Sprint (우선 작업)

1. ✅ ~~OCR 통합~~
2. ✅ ~~Anonymous Auth 개선~~
3. ✅ ~~Profile CRUD~~
4. ✅ ~~Profile 기반 analyze-image~~
5. ✅ ~~프롬프트 분리 및 최적화~~
6. ⏸️ Message History 저장 (2시간)
7. ⏸️ 무료 사용자 일일 제한 (2시간)

**MVP 핵심 기능 완료! 🎉**