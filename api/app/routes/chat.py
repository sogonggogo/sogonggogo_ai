"""
Chat API Routes
"""
from fastapi import APIRouter, HTTPException

from ..models.chat import (
    StartChatRequest,
    StartChatResponse,
    ChatMessageRequest,
    ChatMessageResponse
)
from ..services.session_manager import session_manager

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/start", response_model=StartChatResponse)
async def start_chat(request: StartChatRequest):
    """
    대화 시작
    Args:
        request: 고객 이름
    Returns:
        세션 ID와 인사 메시지
    """
    try:
        session_id, greeting = session_manager.create_session(request.customer_name)

        return StartChatResponse(
            session_id=session_id,
            greeting=greeting
        )

    except Exception as e:
        print(f"[오류] 대화 시작 실패: {e}")
        raise HTTPException(status_code=500, detail=f"대화 시작 실패: {str(e)}")


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    텍스트 메시지 전송
    Args:
        request: 세션 ID 및 텍스트 메시지
    Returns:
        AI 응답 텍스트 및 주문 데이터
    """
    # 세션 확인
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    dialog_manager = session["dialog_manager"]

    try:
        user_text = request.text.strip()

        if not user_text:
            raise HTTPException(status_code=400, detail="텍스트가 비어있습니다.")

        print(f"[세션 {request.session_id}] 사용자 입력: {user_text}")

        # AI 응답 생성
        response_text, order_data = dialog_manager.process_user_input(user_text)

        # 주문 완료 여부 확인
        is_completed = False
        if order_data and "delivery_date" in order_data and order_data["delivery_date"]:
            is_completed = True
            print(f"[세션 {request.session_id}] 주문 완료!")

            # 주문 완료 시 응답이 비어있으면 완료 메시지 추가
            if not response_text or response_text.strip() == "":
                customer_name = session.get("customer_name", "고객")
                response_text = f"{customer_name}님, 주문이 완료되었습니다! 주문하신 내용대로 배송해드리겠습니다. 감사합니다."

        print(f"[세션 {request.session_id}] AI 응답: {response_text}")

        # 대화 히스토리 저장
        session["conversation_history"].append({
            "user": user_text,
            "assistant": response_text,
            "order_data": order_data
        })

        return ChatMessageResponse(
            text=response_text,
            recognized_text=user_text,
            order_data=order_data,
            is_completed=is_completed
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[오류] 메시지 처리 실패: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"메시지 처리 실패: {str(e)}")


@router.post("/reset/{session_id}")
async def reset_chat(session_id: str):
    """
    대화 초기화
    Args:
        session_id: 세션 ID
    Returns:
        성공 메시지
    """
    success = session_manager.delete_session(session_id)

    if not success:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    return {"message": "대화가 초기화되었습니다."}
