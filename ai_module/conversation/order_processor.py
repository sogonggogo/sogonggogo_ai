"""
주문 처리 모듈
DialogManager와 데이터 모델을 연결하여 실제 주문 객체 생성
"""
import uuid
from datetime import datetime
from typing import Dict, Optional
from zoneinfo import ZoneInfo
import sys
import os

# 한국 타임존 설정
KST = ZoneInfo("Asia/Seoul")

# 상위 디렉토리의 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.models import Order, Customer, DinnerMenu, ServingStyle, DINNER_MENUS


class OrderProcessor:
    """주문 처리 클래스"""

    def __init__(self):
        """초기화"""
        self.orders: Dict[str, Order] = {}  # order_id -> Order
        self.customers: Dict[str, Customer] = {}  # customer_name -> Customer

    def create_order_from_dialog(
        self,
        customer_name: str,
        order_data: Dict
    ) -> Optional[Order]:
        """
        대화에서 추출한 정보로 주문 생성
        Args:
            customer_name: 고객 이름
            order_data: DialogManager에서 추출한 주문 데이터
        Returns:
            생성된 Order 객체 또는 None
        """
        try:
            # 디너 메뉴 찾기
            dinner_type = order_data.get("dinner_type")
            if dinner_type not in DINNER_MENUS:
                print(f"오류: '{dinner_type}'는 유효한 디너 타입이 아닙니다.")
                return None

            dinner_menu = DINNER_MENUS[dinner_type]

            # 서빙 스타일 파싱
            serving_style_str = order_data.get("serving_style", "simple")
            try:
                serving_style = ServingStyle(serving_style_str.lower())
            except ValueError:
                print(f"오류: '{serving_style_str}'는 유효한 서빙 스타일이 아닙니다.")
                serving_style = ServingStyle.SIMPLE

            # 주문 생성 (한국 시간 기준)
            order = Order(
                order_id=str(uuid.uuid4())[:8],
                customer_name=customer_name,
                dinner_menu=dinner_menu,
                serving_style=serving_style,
                baguette_count=order_data.get("baguette_count", 3),
                wine_count=order_data.get("wine_count", 0),
                champagne_count=order_data.get("champagne_count", 0),
                delivery_date=order_data.get("delivery_date"),
                created_at=datetime.now(KST),
                status="confirmed"
            )

            # 저장
            self.orders[order.order_id] = order

            # 고객 정보 업데이트
            if customer_name not in self.customers:
                self.customers[customer_name] = Customer(
                    name=customer_name,
                    customer_id=str(uuid.uuid4())[:8]
                )

            self.customers[customer_name].add_order(order)

            return order

        except Exception as e:
            print(f"주문 생성 오류: {e}")
            return None

    def get_order(self, order_id: str) -> Optional[Order]:
        """주문 조회"""
        return self.orders.get(order_id)

    def get_customer_orders(self, customer_name: str) -> list:
        """고객의 주문 내역 조회"""
        customer = self.customers.get(customer_name)
        if customer:
            return customer.order_history
        return []

    def update_order_status(self, order_id: str, status: str) -> bool:
        """주문 상태 업데이트"""
        if order_id in self.orders:
            self.orders[order_id].status = status
            return True
        return False

    def complete_order(self, order_id: str) -> bool:
        """주문 완료 처리"""
        return self.update_order_status(order_id, "completed")

    def get_all_orders(self) -> list:
        """모든 주문 조회"""
        return list(self.orders.values())

    def print_order_summary(self, order: Order):
        """주문 요약 출력"""
        print("\n" + "="*50)
        print(f"주문 ID: {order.order_id}")
        print(f"고객: {order.customer_name}")
        print(f"디너: {order.dinner_menu.name}")
        print(f"서빙 스타일: {order.serving_style.value}")
        print(f"바케트빵: {order.baguette_count}개")
        if order.wine_count > 0:
            print(f"와인: {order.wine_count}병")
        if order.champagne_count > 0:
            print(f"샴페인: {order.champagne_count}병")
        if order.delivery_date:
            print(f"배달 날짜: {order.delivery_date.strftime('%Y년 %m월 %d일')}")
        print(f"주문 시각: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"상태: {order.status}")
        print("="*50 + "\n")
