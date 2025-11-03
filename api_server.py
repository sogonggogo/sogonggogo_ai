"""
FastAPI 서버 - AI 음성 주문 시스템
"""
import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 환경 변수 로드
load_dotenv()

# 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_module'))

from ai_module.voice.speech_recognizer import SpeechRecognizer
from ai_module.conversation.dialog_manager import DialogManager
from ai_module.conversation.order_processor import OrderProcessor

# FastAPI 앱 생성
app = FastAPI(
    title="AI 음성 주문 시스템 API",
    description="고급 디너 음성 주문 시스템",
    version="1.0.0"
)

# CORS 설정 (프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 인스턴스
speech_recognizer = SpeechRecognizer()
dialog_manager = DialogManager()
order_processor = OrderProcessor()

# 세션 저장소 (간단한 메모리 기반)
sessions: Dict[str, Dict[str, Any]] = {}


# ===== Request/Response 모델 =====

class StartOrderRequest(BaseModel):
    customer_name: str

class StartOrderResponse(BaseModel):
    session_id: str
    message: str

class ProcessVoiceRequest(BaseModel):
    session_id: str
    audio_duration: Optional[int] = 5  # 녹음 시간 (초)

class ProcessResponse(BaseModel):
    session_id: str
    user_input: str
    system_response: str
    order_data: Optional[Dict] = None
    is_complete: bool = False

class FinalOrderResponse(BaseModel):
    order_id: str
    customer_name: str
    dinner_menu: str
    dinner_type: str
    serving_style: str
    baguette_count: int
    wine_count: int
    champagne_count: int
    delivery_date: Optional[str]
    created_at: str
    status: str


# ===== API 엔드포인트 =====

@app.get("/")
def root():
    """API 루트"""
    return {
        "message": "AI 음성 주문 시스템 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/order/start", response_model=StartOrderResponse)
def start_order(request: StartOrderRequest):
    """
    주문 시작
    - 고객 이름으로 세션 생성
    - 대화 시작
    """
    import uuid

    session_id = str(uuid.uuid4())[:8]

    # DialogManager 인스턴스 생성 (세션별)
    session_dialog_manager = DialogManager()
    greeting = session_dialog_manager.start_conversation(request.customer_name)

    # 세션 저장
    sessions[session_id] = {
        "customer_name": request.customer_name,
        "dialog_manager": session_dialog_manager,
        "order_data": {},
        "created_at": datetime.now().isoformat()
    }

    return StartOrderResponse(
        session_id=session_id,
        message=greeting
    )


@app.post("/api/order/process-voice", response_model=ProcessResponse)
def process_voice_input(request: ProcessVoiceRequest):
    """
    음성 입력 처리
    - 마이크에서 음성 녹음 및 인식
    - 대화 처리
    """
    # 세션 확인
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    session = sessions[request.session_id]

    # 음성 인식
    user_input = speech_recognizer.recognize_from_microphone(duration=request.audio_duration)

    if not user_input:
        raise HTTPException(status_code=400, detail="음성을 인식할 수 없습니다.")

    # 대화 처리
    session_dialog_manager = session["dialog_manager"]
    response, order_data = session_dialog_manager.process_user_input(user_input)

    # 주문 데이터 업데이트
    if order_data:
        session["order_data"].update(order_data)

    # 주문 완료 여부 확인 (배달 날짜까지 확정되면 완료)
    is_complete = "delivery_date" in session["order_data"] and session["order_data"]["delivery_date"] is not None

    return ProcessResponse(
        session_id=request.session_id,
        user_input=user_input,
        system_response=response,
        order_data=order_data,
        is_complete=is_complete
    )


@app.post("/api/order/finalize/{session_id}", response_model=FinalOrderResponse)
def finalize_order(session_id: str):
    """
    주문 확정
    - 최종 주문 객체 생성
    - JSON 반환
    """
    # 세션 확인
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    session = sessions[session_id]

    # 주문 생성
    order = order_processor.create_order_from_dialog(
        customer_name=session["customer_name"],
        order_data=session["order_data"]
    )

    if not order:
        raise HTTPException(status_code=400, detail="주문 생성에 실패했습니다.")

    # 세션 삭제
    del sessions[session_id]

    # JSON 반환
    order_dict = order.to_dict()
    return FinalOrderResponse(**order_dict)


@app.get("/api/order/session/{session_id}")
def get_session(session_id: str):
    """세션 정보 조회"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    session = sessions[session_id]
    return {
        "session_id": session_id,
        "customer_name": session["customer_name"],
        "order_data": session["order_data"],
        "created_at": session["created_at"]
    }


@app.get("/api/orders")
def get_all_orders():
    """모든 주문 조회"""
    orders = order_processor.get_all_orders()
    return {
        "total": len(orders),
        "orders": [order.to_dict() for order in orders]
    }


@app.get("/health")
def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# ===== 서버 실행 =====
if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("    AI 음성 주문 시스템 API 서버")
    print("="*60)
    print(f"\n서버 주소: http://localhost:8000")
    print(f"API 문서: http://localhost:8000/docs")
    print(f"상태 확인: http://localhost:8000/health")
    print("\n" + "="*60 + "\n")

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 코드 변경 시 자동 재시작
    )
