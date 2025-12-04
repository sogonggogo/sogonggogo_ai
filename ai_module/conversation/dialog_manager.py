"""
대화 관리 모듈 (Groq API + Llama 사용)
고객과의 주문 대화를 처리하고 주문 정보를 추출
"""
import os
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from zoneinfo import ZoneInfo
from groq import Groq

# 한국 타임존 설정
KST = ZoneInfo("Asia/Seoul")


class DialogManager:
    """대화 관리 클래스 (Groq API)"""

    def __init__(self, api_key: Optional[str] = None):
        """
        초기화
        Args:
            api_key: Groq API 키 (None이면 환경변수에서 로드)
        """

        # API 키 로드
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

        # Groq 클라이언트 초기화
        self.client = Groq(api_key=self.api_key)

        # 사용할 모델 (Llama 3.3 70B - 가장 강력함)
        self.model_name = "llama-3.3-70b-versatile"

        self.conversation_history: List[Dict[str, str]] = []
        self.order_context: Dict = {}
        self.customer_name: str = ""

        # 시스템 프롬프트 파일에서 로드
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """
        시스템 프롬프트를 파일에서 로드
        Returns:
            시스템 프롬프트 문자열
        """
        # 현재 파일의 디렉토리 경로
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "system_prompt.txt")

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"시스템 프롬프트 파일을 찾을 수 없습니다: {prompt_path}")
        except Exception as e:
            raise Exception(f"시스템 프롬프트 로드 중 오류 발생: {e}")

    def start_conversation(self, customer_name: str) -> str:
        """
        대화 시작
        Args:
            customer_name: 고객 이름
        Returns:
            인사 메시지
        """
        self.customer_name = customer_name
        self.conversation_history = []

        greeting = f"안녕하세요, {customer_name} 고객님, 어떤 디너를 주문하시겠습니까?"

        return greeting

    def process_user_input(self, user_input: str) -> Tuple[str, Optional[Dict]]:
        """
        사용자 입력 처리
        Args:
            user_input: 사용자 발화
        Returns:
            (응답 메시지, 추출된 주문 정보 또는 None)
        """
        try:
            # 고객 이름과 주문 컨텍스트를 시스템 프롬프트에 추가
            current_system_prompt = self.system_prompt

            # 현재 날짜 추가 (한국 시간 기준)
            today = datetime.now(KST)
            tomorrow = today + timedelta(days=1)
            current_system_prompt += f"\n\n**오늘 날짜:** {today.strftime('%Y년 %m월 %d일')} ({today.strftime('%Y-%m-%d')})\n"
            current_system_prompt += f"**내일 날짜:** {tomorrow.strftime('%Y년 %m월 %d일')} ({tomorrow.strftime('%Y-%m-%d')})\n"

            # 고객 이름 추가
            if self.customer_name:
                current_system_prompt += f"\n**현재 고객:** {self.customer_name}\n"

            # 주문 컨텍스트 추가
            if self.order_context:
                order_info = "\n**현재 주문 상태:**\n"
                for key, value in self.order_context.items():
                    if value:
                        order_info += f"- {key}: {value}\n"
                current_system_prompt += order_info

            # 메시지 구성
            messages = [
                {"role": "system", "content": current_system_prompt}
            ]

            # 대화 히스토리 추가 (최근 6개 턴만)
            for msg in self.conversation_history[-6:]:
                messages.append(msg)

            # 현재 사용자 입력 추가
            messages.append({"role": "user", "content": user_input})

            # Groq API 호출
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=0.3,  # 낮춰서 더 일관된 출력
                max_tokens=200,   # 짧게 답변하도록
                top_p=0.9,
            )

            assistant_message = chat_completion.choices[0].message.content.strip()

            # 대화 기록에 추가
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            # 주문 정보 추출
            order_data = self._extract_order_data(assistant_message)

            # 주문 컨텍스트 업데이트
            if order_data:
                self.update_order_context(order_data)

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
            message: 응답 메시지
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
        '내일', '모레' 등 상대적 표현과 시간 정보도 처리
        기본 시간은 18:00으로 설정
        """
        today = datetime.now(KST)
        base_date = None

        # 1. 기본 날짜 결정 (기본 시간은 18:00으로 설정, 한국 타임존 유지)
        if "모레" in date_str:
            base_date = today.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=2)
        elif "내일" in date_str:
            base_date = today.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif "오늘" in date_str:
            base_date = today.replace(hour=18, minute=0, second=0, microsecond=0)
        else:
            # 특정 날짜 형식 시도
            try:
                parsed = date_parser.parse(date_str, fuzzy=True)
                # 파싱된 날짜의 시간이 00:00이면 18:00으로 설정
                if parsed.hour == 0 and parsed.minute == 0:
                    base_date = parsed.replace(hour=18, minute=0, second=0, microsecond=0)
                else:
                    base_date = parsed
            except:
                return None

        if not base_date:
            return None

        # 2. 시간 정보 추출
        hour = None
        minute = 0

        # "18시", "18시까지", "18:00", "오후 6시" 등의 패턴 매칭
        time_patterns = [
            r'(\d{1,2})시',           # 18시
            r'(\d{1,2}):(\d{2})',     # 18:00
            r'오후\s*(\d{1,2})시?',    # 오후 6시
            r'오전\s*(\d{1,2})시?',    # 오전 6시
        ]

        for pattern in time_patterns:
            match = re.search(pattern, date_str)
            if match:
                if '오후' in date_str:
                    hour = int(match.group(1))
                    if hour != 12:
                        hour += 12
                elif '오전' in date_str:
                    hour = int(match.group(1))
                    if hour == 12:
                        hour = 0
                else:
                    hour = int(match.group(1))
                    if len(match.groups()) > 1:  # "18:00" 형식
                        minute = int(match.group(2))
                break

        # 3. 시간 정보가 명시적으로 있으면 적용 (없으면 기본값 18:00 유지)
        if hour is not None:
            base_date = base_date.replace(hour=hour, minute=minute)

        return base_date

    def update_order_context(self, order_data: Dict):
        """주문 컨텍스트 업데이트"""
        self.order_context.update(order_data)

    def get_order_summary(self) -> str:
        """현재 주문 요약 반환"""
        if not self.order_context:
            return "아직 주문 정보가 없습니다."

        summary_parts = []

        # 기본 정보
        if "dinner_type" in self.order_context:
            summary_parts.append(f"디너: {self.order_context['dinner_type']}")
        if "serving_style" in self.order_context:
            summary_parts.append(f"서빙: {self.order_context['serving_style']} 스타일")

        # 모든 디너 공통 - 스테이크
        if "steak_count" in self.order_context and self.order_context["steak_count"] > 0:
            summary_parts.append(f"스테이크: {self.order_context['steak_count']}개")

        # Valentine Dinner 항목
        if "wine_count" in self.order_context and self.order_context["wine_count"] > 0:
            summary_parts.append(f"와인: {self.order_context['wine_count']}잔")
        if "napkin_count" in self.order_context and self.order_context["napkin_count"] > 0:
            summary_parts.append(f"냅킨: {self.order_context['napkin_count']}개")

        # French Dinner 항목
        if "coffee_cup_count" in self.order_context and self.order_context["coffee_cup_count"] > 0:
            summary_parts.append(f"커피: {self.order_context['coffee_cup_count']}잔")
        if "salad_count" in self.order_context and self.order_context["salad_count"] > 0:
            summary_parts.append(f"샐러드: {self.order_context['salad_count']}인분")

        # English Dinner 항목
        if "egg_scramble_count" in self.order_context and self.order_context["egg_scramble_count"] > 0:
            summary_parts.append(f"에그 스크램블: {self.order_context['egg_scramble_count']}인분")
        if "bacon_count" in self.order_context and self.order_context["bacon_count"] > 0:
            summary_parts.append(f"베이컨: {self.order_context['bacon_count']}인분")
        if "bread_count" in self.order_context and self.order_context["bread_count"] > 0:
            summary_parts.append(f"빵: {self.order_context['bread_count']}개")

        # Champagne Festival Dinner 항목
        if "champagne_count" in self.order_context and self.order_context["champagne_count"] > 0:
            summary_parts.append(f"샴페인: {self.order_context['champagne_count']}병")
        if "baguette_count" in self.order_context:
            summary_parts.append(f"바게트빵: {self.order_context['baguette_count']}개")
        if "coffee_pot_count" in self.order_context and self.order_context["coffee_pot_count"] > 0:
            summary_parts.append(f"커피: {self.order_context['coffee_pot_count']}포트")

        # 인원수 정보
        if "serves_count" in self.order_context:
            summary_parts.append(f"{self.order_context['serves_count']}인분")

        return ", ".join(summary_parts)

    def reset(self):
        """대화 초기화"""
        self.conversation_history = []
        self.order_context = {}
        self.customer_name = ""
