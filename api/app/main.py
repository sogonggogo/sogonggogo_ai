"""
FastAPI Main Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

from .routes import chat_router
from .services.session_manager import session_manager

# 환경 변수 로드
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 생명주기 관리"""
    # 시작 시 실행
    print("\n" + "="*60)
    print("  Dinner Bot Voice API Server Starting...")
    print("="*60)
    print("[알림] Groq API 사용")
    print("       - 음성 인식: Groq Whisper API")
    print("       - 대화 모델: Llama 3.3 70B")
    print("="*60 + "\n")

    yield

    # 종료 시 실행
    print("\n서버 종료 중...")


# FastAPI 앱 초기화
app = FastAPI(
    title="Dinner Bot Voice API",
    description="음성 주문 시스템 API",
    version="1.0.0",
    lifespan=lifespan
)

# 라우터 등록
app.include_router(chat_router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Dinner Bot Voice API Server",
        "version": "1.0.0",
        "endpoints": {
            "start_chat": "POST /api/chat/start",
            "send_message": "POST /api/chat/message",
            "reset_chat": "POST /api/chat/reset/{session_id}"
        }
    }


@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "active_sessions": session_manager.get_active_sessions_count()
    }
