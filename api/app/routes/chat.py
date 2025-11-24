"""
Chat API Routes
"""
import os
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException, Form

from ..models.chat import (
    StartChatRequest,
    StartChatResponse,
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
async def send_message(
    session_id: str = Form(...),
    audio: UploadFile = File(...)
):
    """
    음성 메시지 전송
    Args:
        session_id: 세션 ID
        audio: 오디오 파일 (WAV, MP3 등)
    Returns:
        AI 응답 텍스트 및 주문 데이터
    """
    # 세션 확인
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    speech_recognizer = session["speech_recognizer"]
    dialog_manager = session["dialog_manager"]

    try:
        # 오디오 파일을 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name

        print(f"[세션 {session_id}] 오디오 파일 수신: {audio.filename}")

        # 음성 인식
        recognized_text = speech_recognizer.recognize_from_file(temp_audio_path)

        # 임시 파일 삭제
        os.unlink(temp_audio_path)

        if not recognized_text:
            raise HTTPException(status_code=400, detail="음성을 인식할 수 없습니다.")

        print(f"[세션 {session_id}] 인식된 텍스트: {recognized_text}")

        # AI 응답 생성
        response_text, order_data = dialog_manager.process_user_input(recognized_text)

        print(f"[세션 {session_id}] AI 응답: {response_text}")

        # 대화 히스토리 저장
        session["conversation_history"].append({
            "user": recognized_text,
            "assistant": response_text,
            "order_data": order_data
        })

        # 주문 완료 여부 확인
        is_completed = False
        if order_data and "delivery_date" in order_data and order_data["delivery_date"]:
            is_completed = True
            print(f"[세션 {session_id}] 주문 완료!")

        return ChatMessageResponse(
            text=response_text,
            recognized_text=recognized_text,
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
