from dataclasses import dataclass
from typing import List

PENDING_PAYMENT = "PENDING_PAYMENT"
PAID = "PAID"
CANCELLED = "CANCELLED"

@dataclass
class OrderItemRecord:
    product_id: int      # просто число, а не FK на таблицу другого модуля
    name: str            # снимок названия на момент заказа
    unit_price_cents: int
    qty: int

@dataclass
class OrderRecord:
    id: int
    user_id: int
    status: str
    total_cents: int
    items: List[OrderItemRecord]
