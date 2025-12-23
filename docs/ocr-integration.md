# OCR 서비스 통합 기록

## 개요
Syrano 백엔드에 채팅 스크린샷 텍스트 추출을 위한 OCR 서비스를 통합한 과정.

---

## 시도한 OCR 서비스 비교

| 서비스 | 정확도 | 메모리 | 속도 | 비용 | 결과 |
|--------|--------|--------|------|------|------|
| **EasyOCR** | 90% | 2GB | 10초 | $48/월 (서버) | ❌ 메모리 과다 |
| **PyTesseract** | 60-70% | 150MB | 2초 | $12/월 (서버) | ❌ 정확도 낮음 |
| **Naver Clova OCR** | 95%+ | 0MB | 3초 | 월 100건 무료 | ✅ **채택** |

---

## 최종 선택: Naver Clova OCR

### 선택 이유
- **정확도**: 95%+ (카톡 UI 복잡한 배경 잘 인식)
- **비용**: 월 100건 무료, 초과 시 ₩1/건
- **메모리**: 외부 API 사용으로 서버 메모리 절약
- **속도**: 3초 내외

### 아키텍처
```
Flutter → FastAPI → Naver Clova OCR API → OpenAI LLM → 답변 반환
```

---

## 구현

### 1. Naver Cloud 설정
```bash
# 회원가입
https://www.ncloud.com/

# CLOVA OCR 도메인 생성
Services → AI Services → CLOVA OCR → Domain 생성

# API Gateway 자동 연동
Secret Key 생성 → 자동 연동 클릭
```

### 2. 환경 변수
```env
# .env
NAVER_OCR_SECRET_KEY=xxxxx
NAVER_OCR_INVOKE_URL=https://xxxxx.apigw.ntruss.com/.../general
```

### 3. 코드 구조 (Protocol 패턴)
```
app/services/ocr/
├── __init__.py          # 빈 파일
├── base.py              # OCRService Protocol
└── naver.py             # NaverOCRService 구현체
```

**Protocol 사용 이유:**
- 상속 없는 Duck Typing
- 나중에 다른 OCR 교체 용이
- FastAPI/Python 스타일과 일치

### 4. 핵심 코드

**Protocol 정의:**
```python
# app/services/ocr/base.py
from typing import Protocol

class OCRService(Protocol):
    async def extract_text(self, image_path: str | Path) -> str:
        ...
```

**구현체:**
```python
# app/services/ocr/naver.py
class NaverOCRService:
    def __init__(self, secret_key: str, invoke_url: str):
        self.secret_key = secret_key
        self.invoke_url = invoke_url
    
    async def extract_text(self, image_path: str | Path) -> str:
        # base64 인코딩 → JSON POST
        ...
```

**라우터 사용:**
```python
# app/routers/rizz.py
from app.services.ocr.naver import NaverOCRService
from app.config import NAVER_OCR_SECRET_KEY, NAVER_OCR_INVOKE_URL

ocr_service = NaverOCRService(
    secret_key=NAVER_OCR_SECRET_KEY,
    invoke_url=NAVER_OCR_INVOKE_URL
)
text = await ocr_service.extract_text(image_path)
```

---

## 테스트 결과

### 입력
- 카카오톡 스크린샷 (276KB, PNG)

### OCR 추출
```
추출 블록: 46개
추출 문자: 219자
정확도: 95%+
처리 시간: ~3초
```

### 주요 문장
```
"제가 알림을 꺼둬서 확인이 늦었어요" ✅
"금요일인데 편안한 시간 보내고 계세요??ㅎㅎ" ✅
```

### LLM 답변 생성 성공
```json
{
  "suggestions": [
    "나도 이제 좀 쉬려고 해, 오늘 하루 어땠어?",
    "저녁 맛있게 먹었어? 난 간단히 먹었어ㅎㅎ",
    "프리한 시간 진짜 좋지, 뭐하고 놀아?"
  ]
}
```

---

## 트러블슈팅

### 문제 1: ConnectTimeout
**원인:** `http://` 사용  
**해결:** `https://` 사용

### 문제 2: API Gateway 미연동
**원인:** 내부 Invoke URL 직접 호출 불가  
**해결:** API Gateway 자동 연동 후 Gateway URL 사용

### 문제 3: `/general` 엔드포인트
**원인:** General OCR은 `/general` 경로 필요  
**해결:** URL 끝에 `/general` 추가

---

## 비용 산정

### MVP 단계 (DAU 50명, 월 500건)
```
Naver Clova OCR: 무료 (100건 이내)
API Gateway: 무료 (100만 건 이내)
총: $0/월
```

### 성장기 (DAU 500명, 월 5,000건)
```
Naver Clova OCR: ₩4,000 (~$3)
API Gateway: 무료
총: ~$3/월
```

### 손익분기점
```
월 30,000건 이상: EasyOCR 자체 호스팅이 더 저렴
→ 그 전까지는 Naver Clova 사용 권장
```

---

## 다음 개선 사항
- [ ] Profile 테이블 생성 및 연동
- [ ] OCR 프롬프트 최적화
- [ ] 에러 핸들링 개선
- [ ] 이미지 전처리 (선명도 개선)

---

## 참고 문서
- [Naver Clova OCR 공식 가이드](https://guide.ncloud-docs.com/docs/clovaocr-example01)
- [API Gateway 연동 방법](https://guide.ncloud-docs.com/docs/clovaocr-apigateway)