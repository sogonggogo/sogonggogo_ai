"""
Chat API Pydantic Models
"""
from typing import Dict, Optional
from pydantic import BaseModel


class StartChatRequest(BaseModel):
    """대화 시작 요청"""
    customer_name: str


class StartChatResponse(BaseModel):
    """대화 시작 응답"""
    session_id: str
    greeting: str


class ChatMessageRequest(BaseModel):
    """채팅 메시지 요청"""
    session_id: str
    text: str


class ChatMessageResponse(BaseModel):
    """채팅 메시지 응답"""
    text: str
    recognized_text: Optional[str] = None
    order_data: Optional[Dict] = None
    is_completed: bool = False


class ErrorResponse(BaseModel):
    """에러 응답"""
    error: str
    detail: Optional[str] = None
