"""
데이터 모델 클래스
프론트/백과 연동 시 API 응답 형식으로 사용 가능
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class ServingStyle(Enum):
    """서빙 스타일"""
    SIMPLE = "simple"
    GRAND = "grand"
    DELUXE = "deluxe"


class DinnerType(Enum):
    """디너 타입"""
    VALENTINE = "발렌타인 디너"
    FRENCH = "프렌치 디너"
    ENGLISH = "잉글리시 디너"
    CHAMPAGNE = "샴페인 축제 디너"


@dataclass
class DinnerMenu:
    """디너 메뉴"""
    name: str
    dinner_type: DinnerType
    base_ingredients: Dict[str, int]  # {재료명: 수량}
    description: str = ""

    def __post_init__(self):
        if isinstance(self.dinner_type, str):
            self.dinner_type = DinnerType(self.dinner_type)


@dataclass
class Order:
    """주문 정보"""
    order_id: str
    customer_name: str
    dinner_menu: DinnerMenu
    serving_style: ServingStyle
    baguette_count: int = 3  # 기본 3개
    wine_count: int = 0
    champagne_count: int = 0
    delivery_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, confirmed, completed

    def __post_init__(self):
        if isinstance(self.serving_style, str):
            self.serving_style = ServingStyle(self.serving_style)

    def to_dict(self) -> Dict:
        """딕셔너리로 변환 (API 응답용)"""
        return {
            "order_id": self.order_id,
            "customer_name": self.customer_name,
            "dinner_menu": self.dinner_menu.name,
            "dinner_type": self.dinner_menu.dinner_type.value,
            "serving_style": self.serving_style.value,
            "baguette_count": self.baguette_count,
            "wine_count": self.wine_count,
            "champagne_count": self.champagne_count,
            "delivery_date": self.delivery_date.isoformat() if self.delivery_date else None,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }

    def get_summary(self) -> str:
        """주문 요약 문자열"""
        items = [
            f"디너: {self.dinner_menu.name}",
            f"서빙: {self.serving_style.value} 스타일",
            f"바케트빵: {self.baguette_count}개"
        ]
        if self.wine_count > 0:
            items.append(f"와인: {self.wine_count}병")
        if self.champagne_count > 0:
            items.append(f"샴페인: {self.champagne_count}병")

        return ", ".join(items)


@dataclass
class Customer:
    """고객 정보"""
    name: str
    customer_id: Optional[str] = None
    order_history: List[Order] = field(default_factory=list)

    def add_order(self, order: Order):
        """주문 추가"""
        self.order_history.append(order)


# 디너 메뉴 샘플 데이터
DINNER_MENUS = {
    "발렌타인 디너": DinnerMenu(
        name="발렌타인 디너",
        dinner_type=DinnerType.VALENTINE,
        base_ingredients={
            "고기": 2,
            "채소": 3,
            "와인": 1,
            "바케트빵": 3,
            "계란": 4
        },
        description="로맨틱한 발렌타인데이를 위한 특별한 디너"
    ),
    "프렌치 디너": DinnerMenu(
        name="프렌치 디너",
        dinner_type=DinnerType.FRENCH,
        base_ingredients={
            "고기": 3,
            "채소": 4,
            "와인": 1,
            "바케트빵": 3,
            "계란": 3
        },
        description="정통 프랑스 요리 스타일의 고급 디너"
    ),
    "잉글리시 디너": DinnerMenu(
        name="잉글리시 디너",
        dinner_type=DinnerType.ENGLISH,
        base_ingredients={
            "고기": 4,
            "채소": 2,
            "와인": 1,
            "바케트빵": 3,
            "계란": 2
        },
        description="영국 전통 스타일의 풍성한 디너"
    ),
    "샴페인 축제 디너": DinnerMenu(
        name="샴페인 축제 디너",
        dinner_type=DinnerType.CHAMPAGNE,
        base_ingredients={
            "고기": 3,
            "채소": 5,
            "샴페인": 1,
            "바케트빵": 3,
            "계란": 4
        },
        description="특별한 축하를 위한 샴페인과 함께하는 디너"
    )
}
