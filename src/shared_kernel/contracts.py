"""Контракты событий между модулями. Лежат в SharedKernel, чтобы издатель и
подписчик не импортировали друг друга (разрыв циклических зависимостей)."""
from dataclasses import dataclass
from .events import DomainEvent

@dataclass(frozen=True)
class OrderCreatedEvent(DomainEvent):
    order_id: int
    user_id: int
    amount_cents: int

@dataclass(frozen=True)
class PaymentSucceededEvent(DomainEvent):
    order_id: int
    invoice_id: int

@dataclass(frozen=True)
class PaymentFailedEvent(DomainEvent):
    order_id: int
    reason: str
