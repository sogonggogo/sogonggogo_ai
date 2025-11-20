# AI 음성 주문 시스템 (소공고고 AI)

고급 디너 음성 주문 시스템의 AI 음성인식 모듈 - FastAPI 서버

## 주요 기능

### 1. 음성인식 모듈 (`ai_module/voice/`)
- **Faster-Whisper** (OpenAI Whisper 오픈소스 모델) 사용
- 로컬에서 실행, 완전 무료
- 마이크 입력을 텍스트로 변환
- 한국어 음성 인식 지원


### 2. 대화 처리 모듈 (`ai_module/conversation/`)
- **DialogManager**: vLLM (로컬 LLM 서버)을 활용한 자연어 대화 처리
  - 완전 무료, 로컬 실행 (외부 API 호출 없음)
  - 오픈소스 LLM 사용 (Llama-3-Korean, EEVE 등)
  - 순수 한국어 대화 지원 (외국어 혼용 방지)
  - 고객의 의도 파악
  - 디너 추천 및 서빙 스타일 제안
  - 주문 정보 추출 (JSON 형식)
  - 자연스러운 대화 흐름 관리
  - 배달 날짜 확정 시 자동 주문 완료
  - RTX 4060 8GB VRAM 최적화

- **OrderProcessor**: 주문 데이터 관리
  - 주문 생성
  - 고객 정보 관리
  - 주문 내역 조회



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

시스템: 네, 김고객 고객님, 디너는 샴페인 축제 디너, 서빙은 디럭스 스타일로 주문하셨습니다. 맞으시죠?
고객: 바케트빵을 6개로, 샴페인을 2병으로 추가해주세요.

시스템: 알겠습니다. 바케트빵 6개, 샴페인 2병으로 추가하겠습니다. 추가로 필요하신 것 있으세요?
고객: 없어요.

시스템: 배달 날짜는 언제로 해드릴까요?
고객: 내일이요.

시스템: 네, 내일 배달해드리겠습니다. 주문해주셔서 감사합니다!

[주문 완료] 주문이 성공적으로 접수되었습니다!

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

## 설치 및 실행 가이드

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. vLLM 로컬 서버 실행

**필수:** FastAPI 서버를 실행하기 전에 vLLM 서버를 먼저 실행해야 합니다.

```bash
# RTX 4060 8GB 최적화 설정
vllm serve beomi/Llama-3-Open-Ko-8B \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype half \
  --max-model-len 2048 \
  --gpu-memory-utilization 0.9
```

자세한 설정 방법은 [VLLM_SETUP_GUIDE.md](VLLM_SETUP_GUIDE.md)를 참고하세요.

### 3. FastAPI 서버 실행
```bash
uvicorn main:app --reload --port 8080
```

**주의:** vLLM 서버(8000번 포트)와 FastAPI 서버(8080번 포트)는 다른 포트를 사용합니다.

---

## 비용 및 라이선스

### ✅ 완전 무료
- **음성인식**: Faster-Whisper (오픈소스, 로컬)
- **대화 처리**: vLLM + 오픈소스 LLM (로컬)
- **외부 API 호출**: 없음
- **비용**: 0원 (전기세/서버 비용만)

### 🔒 프라이버시
- 모든 데이터가 로컬에서만 처리
- 외부 서버로 전송 없음
- 완벽한 프라이버시 보장

---

## 시스템 요구사항

### 최소 사양
- Python 3.8 이상
- CPU: 멀티코어 프로세서
- RAM: 16GB 이상
- GPU: 선택사항 (CPU만으로도 가능하지만 느림)

### 권장 사양 (RTX 4060 8GB 기준)
- Python 3.10 이상
- GPU: NVIDIA RTX 4060 8GB
- RAM: 16GB 이상
- CUDA: 11.8 이상
- 응답 속도: 1-3초

---

## 문제 해결

문제가 발생하면 [VLLM_SETUP_GUIDE.md](VLLM_SETUP_GUIDE.md)의 트러블슈팅 섹션을 참고하세요.