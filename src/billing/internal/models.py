from dataclasses import dataclass
from typing import Optional

ISSUED, PAID, FAILED = "ISSUED", "PAID", "FAILED"

@dataclass
class InvoiceRecord:
    id: int
    order_id: int       # просто число-ссылка; таблицы Orders Billing недоступны
    user_id: int
    amount_cents: int
    status: str
    reason: Optional[str]
