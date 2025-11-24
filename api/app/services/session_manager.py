"""
Session Manager Service
"""
import uuid
from typing import Dict, Optional

from ai_module.voice.speech_recognizer import SpeechRecognizer
from ai_module.conversation.dialog_manager import DialogManager


class SessionManager:
    """세션 관리 클래스"""

    def __init__(self):
        self.sessions: Dict[str, Dict] = {}

    def create_session(self, customer_name: str) -> tuple[str, str]:
        """
        새로운 세션 생성
        Args:
            customer_name: 고객 이름
        Returns:
            (session_id, greeting)
        """
        # 세션 ID 생성
        session_id = str(uuid.uuid4())

        # 음성 인식기 초기화
        speech_recognizer = SpeechRecognizer()

        # 대화 관리자 초기화
        dialog_manager = DialogManager()

        # 대화 시작
        greeting = dialog_manager.start_conversation(customer_name)

        # 세션 저장
        self.sessions[session_id] = {
            "customer_name": customer_name,
            "speech_recognizer": speech_recognizer,
            "dialog_manager": dialog_manager,
            "conversation_history": []
        }

        print(f"[세션 생성] {session_id} - {customer_name}")

        return session_id, greeting

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        세션 조회
        Args:
            session_id: 세션 ID
        Returns:
            세션 데이터 또는 None
        """
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """
        세션 삭제
        Args:
            session_id: 세션 ID
        Returns:
            성공 여부
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            print(f"[세션 삭제] {session_id}")
            return True
        return False

    def get_active_sessions_count(self) -> int:
        """활성 세션 수 반환"""
        return len(self.sessions)


# 싱글톤 인스턴스
session_manager = SessionManager()
