# AI 음성 주문 시스템 (소공고고 AI)

고급 디너 음성 주문 시스템의 AI 음성인식 모듈 - FastAPI 서버

## 주요 기능

### 1. 음성인식 모듈 (`ai_module/voice/`)
- Google Cloud Speech-to-Text API를 사용한 실시간 음성인식
- 마이크 입력을 텍스트로 변환


### 2. 대화 처리 모듈 (`ai_module/conversation/`)
- **DialogManager**: OpenAI GPT를 활용한 자연어 대화 처리
  - 고객의 의도 파악
  - 디너 추천
  - 주문 정보 추출
  - 주문 확인

- **OrderProcessor**: 주문 데이터 관리
  - 주문 생성
  - 고객 정보 관리
  - 주문 내역 조회


## 실행 방법

### 1. 환경 설정
```bash
# 라이브러리 설치
pip install -r requirements.txt

# .env 파일에 API 키 설정
OPENAI_API_KEY=your_openai_key
GOOGLE_APPLICATION_CREDENTIALS=config/your-google-key.json
```

### 2. 서버 실행
```bash
python api_server.py
```

서버 실행 후:
- **API 서버**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **헬스 체크**: http://localhost:8000/health


### 데모 시나리오 예시

```
POST /api/order/start
→ session_id 받기

POST /api/order/process-voice (반복)
→ 음성 입력 → 대화 진행

시스템: 안녕하세요, 김고객 고객님, 어떤 디너를 주문하시겠습니까?
고객: 맛있는 디너 추천해주세요.

시스템: 무슨 기념일인가요?
고객: 내일이 어머님 생신이에요

시스템: 정말 축하드려요. 프렌치 디너 또는 샴페인 축제 디너는 어떠세요?
고객: 샴페인 축제 디너 좋겠어요.

시스템: 샴페인 축제 디너 알겠습니다. 그리고 서빙은 디럭스 스타일 어떨까요?
고객: 네, 디럭스 스타일 좋아요.

시스템: 네, 김고객 고객님, 디너는 샴페인 축제 디너, 서빙은 디럭스 스타일로 주문하셨습니다.
고객: 바케트빵을 6개로, 샴페인을 2병으로 변경해요.

시스템: 네, 김고객 고객님, 디너는 샴페인 축제 디너, 서빙은 디럭스 스타일, 바케트빵 6개, 샴페인 2병 주문하셨습니다.
고객: 맞아요.

시스템: 추가로 필요하신 것 있으세요?
고객: 없어요.

시스템: 내일 주문하신대로 보내드리겠습니다. 감사합니다.

POST /api/order/finalize/{session_id}
→ 최종 JSON 받기
```

## API 연동 가이드

주문 완료 시 JSON 형식으로 반환됩니다:

```json
{
  "order_id": "abc123",
  "customer_name": "김고객",
  "dinner_menu": "샴페인 축제 디너",
  "dinner_type": "샴페인 축제 디너",
  "serving_style": "deluxe",
  "baguette_count": 6,
  "wine_count": 0,
  "champagne_count": 2,
  "delivery_date": "2025-11-04T00:00:00",
  "created_at": "2025-11-03T18:30:00",
  "status": "confirmed"
}
```
