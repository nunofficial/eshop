from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductRecord:
    id: int
    name: str
    price_cents: int
    stock: int
    category_id: Optional[int]
