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

### 4. 사용량 제한 구현 ✅ **완료**

**완료 내용:**
- Subscription 모델에 `daily_usage_count`, `last_reset_date` 추가
- `check_and_increment_usage` 서비스 함수 구현
- `UsageInfo` 스키마 추가 (remaining, limit, is_premium)
- 무료: 5회/일, 프리미엄: 무제한
- 응답에 사용량 정보 포함
- `/rizz/generate`, `/rizz/analyze-image` 모두 적용
- 자정 자동 리셋

**테스트 완료:**
- ✅ 무료 5회 제한
- ✅ 6회차 429 에러
- ✅ 프리미엄 전환 후 무제한

---

**MVP 핵심 기능 완료! 🎉**

---

## 🟡 Medium Priority (MVP 이후)

### 5. 로깅 개선 및 보안 강화
**상태:** ⏸️ 대기

**현재 문제:**
- OCR 추출 텍스트 전체가 로그에 남음 (개인 대화 내용 노출)
- 로그 파일 크기 증가
- 프로덕션 환경에서 개인정보 보호 이슈

**개선 방향:**
1. **개발 환경:** 전체 텍스트 로그 유지 (디버깅용)
2. **프로덕션:** 프리뷰만 (100자) 또는 완전 제거
3. **환경변수로 제어:**
```python
   DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
   
   if DEBUG_MODE:
       logger.info(f"전체 추출 텍스트:\n{conversation}")
   else:
       logger.info(f"Extracted text preview: {conversation[:100]}...")
```

**Sentry 연동 시:**
- 에러만 Sentry로 전송
- 민감한 정보(대화 내용)는 제외

**예상 시간:** 1시간

---

### 6. 프롬프트 A/B 테스트
**상태:** ⏸️ 대기

**내용:**
- 다양한 프롬프트 버전 테스트
- 사용자 피드백 수집
- 실사용 데이터 기반 프롬프트 개선

**예상 시간:** 3시간

---

### 7. 만료된 구독 자동 처리
**상태:** ⏸️ 대기

**내용:**
- `expires_at` 체크 로직 추가
- Cron job으로 만료된 구독 자동 `is_premium=False` 처리
- 또는 요청 시점에 체크

**예상 시간:** 2시간

---

## 🟢 Low Priority (나중에)

### 8. Message History 본격 활용 (필요시)
**상태:** ⏸️ 보류

**현재 판단:**
- 응답 품질 개선 효과 거의 없음
- Profile 정보만으로도 충분히 개인화됨
- 테이블은 준비되어 있으니 필요하면 활용

**미래 가능성:**
- 사용자가 선택한 답장 패턴 학습
- 대화 스타일 장기 학습
- 개인화 추천 강화

**조건:**
- 실사용 데이터로 효과 검증 후
- 명확한 사용 시나리오 확인 후

---

### 9. 실제 결제 연동
**내용:**
- App Store / Google Play 영수증 검증
- Subscription 만료 체크 자동화
- 환불 처리

---

### 10. OCR 이미지 전처리
**내용:**
- 저화질 이미지 개선
- 텍스트 영역 자동 크롭
- 이미지 회전 보정

---

### 11. CORS 프로덕션 설정
**내용:**
- `allow_origins` 실제 도메인으로 제한
- 프로덕션 환경변수 분리

---

### 12. 구조화된 로깅
**내용:**
- JSON 형식 로깅
- 에러 추적 강화
- 로그 레벨 세분화

---

## 📊 Progress Tracker

### MVP 완료 ✅
- [x] Anonymous Auth API 개선
- [x] Profile CRUD 구현
- [x] Profile 기반 analyze-image 개선
- [x] 프롬프트 분리 및 최적화
- [x] 사용량 제한 구현 (5/day free, unlimited premium)

### 다음 단계 (우선순위순)
- [ ] 로깅 개선 및 보안 강화 ⏸️
- [ ] 프롬프트 A/B 테스트 ⏸️
- [ ] 만료된 구독 자동 처리 ⏸️

### 보류/저순위
- [ ] Message History 본격 활용 (보류)
- [ ] 실제 결제 연동
- [ ] OCR 이미지 전처리
- [ ] CORS 프로덕션 설정
- [ ] 구조화된 로깅

---

## 🎯 Next Sprint (우선 작업)

1. ✅ ~~OCR 통합~~
2. ✅ ~~Anonymous Auth 개선~~
3. ✅ ~~Profile CRUD~~
4. ✅ ~~Profile 기반 analyze-image~~
5. ✅ ~~프롬프트 분리 및 최적화~~
6. ✅ ~~사용량 제한 구현~~

**백엔드 MVP 완성! 프론트엔드 개발 시작 가능! 🚀**