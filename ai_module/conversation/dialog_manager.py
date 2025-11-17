"""
대화 관리 모듈 (Groq API - Llama 활용)
고객과의 주문 대화를 처리하고 주문 정보를 추출
"""
import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from groq import Groq
from dateutil import parser as date_parser


class DialogManager:
    """대화 관리 클래스"""

    def __init__(self, api_key: Optional[str] = None):
        """
        초기화
        Args:
            api_key: Groq API 키
        """
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.conversation_history: List[Dict[str, str]] = []
        self.order_context: Dict = {}
        self.customer_name: str = ""

        # 시스템 프롬프트
        self.system_prompt = """당신은 고급 디너 주문을 받는 친절한 AI 어시스턴트입니다.

**절대 규칙: 오직 한국어로만 대화하세요. 영어, 중국어, 일본어, 러시아어, 독일어 등 어떤 외국어 단어도 절대 사용하지 마세요. 모든 단어는 순수 한글로만 표현하세요.**

**대화 흐름:**
1. 고객이 디너 종류를 물어보면 → 4가지 디너 종류를 간단히 소개하고 "무슨 기념일인가요?" 질문
2. 고객이 기념일을 먼저 말하면 → 축하 + 기념일에 맞는 디너 2개 추천 (예: "프렌치 디너 또는 샴페인 축제 디너는 어떠세요?")
3. 고객이 디너를 선택하면 → 서빙 스타일 3가지(심플, 그랜드, 디럭스)를 설명하고 추천
4. 고객이 서빙을 선택하면 → 주문 내용 전체 확인 (예: "디너는 샴페인 축제 디너, 서빙은 디럭스 스타일로 주문하셨습니다. 맞으시죠?")
5. 고객이 수정을 요청하면 → 수정 내용 반영 후 전체 주문 다시 확인
6. 고객이 확인하면 → "바케트빵이나 와인/샴페인 추가하시겠어요?" 또는 "추가로 필요하신 것 있으세요?" 질문
7. 고객이 "없어요"라고 하면 → 배달 날짜 물어보고 주문 완료

**주문 정보:**
- 디너 종류: 발렌타인 디너, 프렌치 디너, 잉글리시 디너, 샴페인 축제 디너
- 서빙 스타일: 심플(simple), 그랜드(grand), 디럭스(deluxe)
- 바케트빵: 기본 3개 (고객이 원하는 개수로 변경 가능, 1개부터 가능)
- 와인/샴페인: 기본 1병 (고객이 원하는 개수로 변경 가능, 0개도 가능)
- 배달 날짜: "내일" → 다음날, "모레" → 2일 후

**대화 규칙:**
- 한 번에 한 가지만 질문하세요
- 짧고 명확하게 응답하세요 (1-2문장)
- 고객 이름을 자주 사용하세요
- 주문 확인 시 전체 내용을 나열하세요
- 기념일에 진심으로 축하해주세요
- 고객이 요청한 수량은 그대로 반영하세요 (임의로 변경하지 마세요)
- 외국어를 절대 사용하지 마세요. 예: richtig(X) → 맞습니다(O), 豪華(X) → 화려한(O)

**주문 정보가 확정되면 다음 JSON을 응답 끝에 추가:**
[ORDER_DATA]
{
    "dinner_type": "샴페인 축제 디너",
    "serving_style": "deluxe",
    "baguette_count": 6,
    "wine_count": 0,
    "champagne_count": 2,
    "delivery_date": "2025-11-04"
}
[/ORDER_DATA]

**중요:** 디너 종류와 서빙 스타일이 모두 결정된 직후에는 반드시 ORDER_DATA를 포함하세요.
"""

    def start_conversation(self, customer_name: str) -> str:
        """
        대화 시작
        Args:
            customer_name: 고객 이름
        Returns:
            인사 메시지
        """
        self.customer_name = customer_name
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]

        greeting = f"안녕하세요, {customer_name} 고객님, 어떤 디너를 주문하시겠습니까?"
        self.conversation_history.append({"role": "assistant", "content": greeting})

        return greeting

    def process_user_input(self, user_input: str) -> Tuple[str, Optional[Dict]]:
        """
        사용자 입력 처리
        Args:
            user_input: 사용자 발화
        Returns:
            (응답 메시지, 추출된 주문 정보 또는 None)
        """
        # 대화 기록에 추가
        self.conversation_history.append({"role": "user", "content": user_input})

        # Groq API 호출 (Llama 3.3 70B 모델 사용)
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=self.conversation_history,
                temperature=0.5,  # 더 일관된 응답을 위해 낮춤
                max_tokens=500
            )

            assistant_message = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            # 주문 정보 추출
            order_data = self._extract_order_data(assistant_message)

            # 주문 데이터 부분 제거한 깨끗한 응답
            clean_response = assistant_message.split("[ORDER_DATA]")[0].strip()

            return clean_response, order_data

        except Exception as e:
            error_msg = f"죄송합니다. 오류가 발생했습니다: {e}"
            return error_msg, None

    def _extract_order_data(self, message: str) -> Optional[Dict]:
        """
        메시지에서 주문 데이터 추출
        Args:
            message: GPT 응답 메시지
        Returns:
            주문 데이터 딕셔너리 또는 None
        """
        try:
            if "[ORDER_DATA]" in message and "[/ORDER_DATA]" in message:
                start = message.index("[ORDER_DATA]") + len("[ORDER_DATA]")
                end = message.index("[/ORDER_DATA]")
                json_str = message[start:end].strip()
                order_data = json.loads(json_str)

                # 날짜 파싱
                if "delivery_date" in order_data and order_data["delivery_date"]:
                    order_data["delivery_date"] = self._parse_date(order_data["delivery_date"])

                return order_data

        except Exception as e:
            print(f"주문 데이터 추출 오류: {e}")

        return None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        날짜 문자열을 datetime으로 변환
        '내일', '모레' 등 상대적 표현도 처리
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if "내일" in date_str:
            return today + timedelta(days=1)
        elif "모레" in date_str:
            return today + timedelta(days=2)
        elif "오늘" in date_str:
            return today
        else:
            try:
                return date_parser.parse(date_str)
            except:
                return None

    def update_order_context(self, order_data: Dict):
        """주문 컨텍스트 업데이트"""
        self.order_context.update(order_data)

    def get_order_summary(self) -> str:
        """현재 주문 요약 반환"""
        if not self.order_context:
            return "아직 주문 정보가 없습니다."

        summary_parts = []
        if "dinner_type" in self.order_context:
            summary_parts.append(f"디너: {self.order_context['dinner_type']}")
        if "serving_style" in self.order_context:
            summary_parts.append(f"서빙: {self.order_context['serving_style']} 스타일")
        if "baguette_count" in self.order_context:
            summary_parts.append(f"바케트빵: {self.order_context['baguette_count']}개")
        if "wine_count" in self.order_context and self.order_context["wine_count"] > 0:
            summary_parts.append(f"와인: {self.order_context['wine_count']}병")
        if "champagne_count" in self.order_context and self.order_context["champagne_count"] > 0:
            summary_parts.append(f"샴페인: {self.order_context['champagne_count']}병")

        return ", ".join(summary_parts)

    def reset(self):
        """대화 초기화"""
        self.conversation_history = []
        self.order_context = {}
        self.customer_name = ""
