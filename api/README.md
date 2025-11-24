# Dinner Bot Voice API

음성 주문 시스템 FastAPI 서버

## 폴더 구조

```
api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 초기화
│   ├── models/              # Pydantic 모델
│   │   ├── __init__.py
│   │   └── chat.py
│   ├── routes/              # API 엔드포인트
│   │   ├── __init__.py
│   │   └── chat.py
│   └── services/            # 비즈니스 로직
│       ├── __init__.py
│       └── session_manager.py
├── run.py                   # 서버 실행
└── README.md
```

## 실행 방법

### 1. 서버 시작

```bash
cd api
python run.py
```

### 2. 접속

- **서버**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs (Swagger UI)

## API 엔드포인트

### 1. 대화 시작
- **POST** `/api/chat/start`
- Request: `{ "customer_name": "김동환" }`
- Response: `{ "session_id": "...", "greeting": "..." }`

### 2. 음성 메시지 전송
- **POST** `/api/chat/message`
- Request: FormData (session_id, audio)
- Response: `{ "text": "...", "recognized_text": "...", "order_data": {...}, "is_completed": false }`

### 3. 대화 초기화
- **POST** `/api/chat/reset/{session_id}`
- Response: `{ "message": "..." }`

### 4. 헬스 체크
- **GET** `/api/health`
- Response: `{ "status": "healthy", "active_sessions": 0 }`

## 상세 문서

자세한 API 명세는 [API_SPEC.md](../API_SPEC.md) 참고
