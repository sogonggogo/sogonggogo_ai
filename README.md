# 🍽️ 소공고고 AI - 디너 주문 챗봇

미스터 대박 디너 주문을 위한 AI 챗봇 시스템

## 📁 프로젝트 구조

```
sogonggogo_ai/
├── ai_module/                        # 핵심 AI 모듈
│   ├── conversation/                 # 대화 관리
│   │   ├── dialog_manager.py        # Groq API 대화 관리자
│   │   └── system_prompt.txt        # 시스템 프롬프트
│   └── voice/                        # 음성 인식
│       └── speech_recognizer.py     # Groq Whisper API
│
├── api/                              # FastAPI 서버
│   ├── app/
│   │   ├── main.py                  # FastAPI 앱
│   │   ├── models/                  # Pydantic 모델
│   │   ├── routes/                  # API 라우트
│   │   └── services/                # 비즈니스 로직
│   ├── run.py                       # 서버 실행
│   └── README.md
│
├── test/                             # 테스트 스크립트
│   ├── test_text_chat.py            # 텍스트 채팅 테스트
│   └── test_voice_chat.py           # 음성 채팅 테스트
│
├── .env                              # 환경 변수 (GROQ_API_KEY)
├── API_SPEC.md                       # API 명세서
└── requirements.txt                  # 의존성
```

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. Groq API 키 설정

`.env` 파일에 Groq API 키를 설정하세요:

```bash
GROQ_API_KEY=your_api_key_here
```


### 3. 모듈 사용

```python
from ai_module.conversation.dialog_manager import DialogManager

# Groq API 대화 관리자 초기화
dm = DialogManager()

# 대화 시작
greeting = dm.start_conversation("홍길동")
print(greeting)  # "안녕하세요, 홍길동 고객님, 어떤 디너를 주문하시겠습니까?"

# 사용자 입력 처리
response, order_data = dm.process_user_input("맛있는 디너 추천해주세요")
print(response)  # "무슨 기념일인가요?"
```

### 4. 테스트 실행

```bash
# 텍스트 챗봇 테스트
python test/test_text_chat.py

# 음성 챗봇 테스트 (Groq Whisper API)
python test/test_voice_chat.py
```

### 5. API 서버 실행

```bash
cd api
python run.py
```

서버 접속:
- **서버**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 🤖 모델 정보

### LLM (대화 모델)
- **모델**: Llama 3.3 70B Versatile
- **제공**: Groq API (클라우드 기반)

### 음성 인식
- **모델**: Whisper Large v3 Turbo
- **제공**: Groq API (클라우드 기반)


## 📋 메뉴 정보

### 디너 종류
1. **발렌타인 디너** - 하트 장식, 와인+스테이크
   - 서빙: 심플, 그랜드, 디럭스
2. **프렌치 디너** - 커피, 와인, 샐러드, 스테이크
   - 서빙: 심플, 그랜드, 디럭스
3. **잉글리시 디너** - 에그 스크램블, 베이컨, 빵, 스테이크
   - 서빙: 심플, 그랜드, 디럭스
4. **샴페인 축제 디너** - 샴페인, 바게트빵, 커피, 와인, 스테이크 (2인)
   - 서빙: **그랜드, 디럭스만** (심플 불가)

### 서빙 스타일
1. **심플** - 플라스틱 접시/컵, 종이 냅킨
2. **그랜드** - 도자기 접시/컵, 흰색 면 냅킨
3. **디럭스** - 도자기 접시/컵, 린넨 냅킨, 꽃병 포함

## 🔄 대화 흐름 (데모 시나리오)

```
시스템: 안녕하세요, OOO 고객님, 어떤 디너를 주문하시겠습니까?
고객: 맛있는 디너 추천해주세요.

시스템: 무슨 기념일인가요?
고객: 내일이 어머님 생신이에요

시스템: 정말 축하드려요. 프렌치 디너 또는 샴페인 축제 디너는 어떠세요?
고객: 샴페인 축제 디너 좋겠어요.

시스템: 샴페인 축제 디너 좋은 선택이십니다! 서빙은 그랜드 스타일과 디럭스 스타일 중 어떤 것이 좋으실까요?
고객: 네, 디럭스 스타일 좋아요.

시스템: 네, OOO 고객님, 디너는 샴페인 축제 디너, 서빙은 디럭스 스타일로 주문하셨습니다.
고객: 그리고 바케트빵을 6개로, 샴페인을 2병으로 변경해요.

시스템: 네, OOO 고객님, 디너는 샴페인 축제 디너, 서빙은 디럭스 스타일, 바케트빵 6개, 샴페인 2병 주문하셨습니다.
고객: 맞아요.

시스템: 추가로 필요하신 것 있으세요?
고객: 없어요.

시스템: 언제 배달해드릴까요?
고객: 내일이요.

시스템: 내일에 주문하신대로 보내드리겠습니다. 감사합니다.
```

## 💾 주문 데이터 형식

```json
{
    "dinner_type": "샴페인 축제 디너",
    "serving_style": "deluxe",
    "baguette_count": 6,
    "wine_count": 1,
    "steak_count": 2,
    "champagne_count": 2,
    "serves_count": 2,
    "delivery_date": "2025-11-26T18:00:00"
}
```

## 기술 스택
- **Backend**: FastAPI, Pydantic, Python 3.11
- **AI**: Groq API (Llama 3.3, Whisper v3 Turbo)
- **Audio**: PyAudio (음성 입력)
- **Utils**: python-dateutil (날짜 파싱)

## 📡 API 아키텍처

### 엔드포인트
1. **POST /api/chat/start** - 대화 시작, 세션 생성
2. **POST /api/chat/message** - 음성 파일 전송, AI 응답 수신
3. **POST /api/chat/reset/{session_id}** - 세션 초기화
4. **GET /api/health** - 서버 상태 확인

### 데이터 흐름
```
프론트엔드 → 음성 녹음 → FormData 전송
    ↓
FastAPI 서버 → Groq Whisper API (STT)
    ↓
Dialog Manager → Groq Llama API (대화)
    ↓
주문 데이터 추출 → JSON 반환
    ↓
프론트엔드 ← 응답 수신 (텍스트 + 주문 정보)
```
