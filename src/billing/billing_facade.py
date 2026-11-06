from dataclasses import dataclass
from typing import Optional
from src.shared_kernel import (connect, NotFoundError, EventBus,
                               OrderCreatedEvent, PaymentSucceededEvent, PaymentFailedEvent)
from .internal.gateway import FakePaymentGateway
from .internal.models import PAID, FAILED
from .internal.repository import InvoiceRepository

@dataclass(frozen=True)
class InvoiceDTO:
    id: int
    order_id: int
    amount_cents: int
    status: str
    reason: Optional[str]

class BillingFacade:
    """Публичный API модуля Billing.
    Не импортирует Orders: подписывается на OrderCreatedEvent из SharedKernel."""
    def __init__(self, bus: EventBus, gateway: Optional[FakePaymentGateway] = None,
                 db_path: str = ":memory:") -> None:
        self._bus = bus
        self._gateway = gateway or FakePaymentGateway()
        self._repo = InvoiceRepository(connect(db_path))
        bus.subscribe(OrderCreatedEvent, self._on_order_created)

    def get_invoice_by_order(self, order_id: int) -> InvoiceDTO:
        inv = self._repo.get_by_order(order_id)
        if not inv:
            raise NotFoundError(f"Счёт для заказа {order_id} не найден")
        return InvoiceDTO(inv.id, inv.order_id, inv.amount_cents, inv.status, inv.reason)

    def _on_order_created(self, e: OrderCreatedEvent) -> None:
        if self._repo.get_by_order(e.order_id):      # идемпотентность
            return
        inv = self._repo.add(e.order_id, e.user_id, e.amount_cents)
        ok, reason = self._gateway.charge(e.amount_cents)
        if ok:
            self._repo.set_status(inv.id, PAID)
            self._bus.publish(PaymentSucceededEvent(e.order_id, inv.id))
        else:
            self._repo.set_status(inv.id, FAILED, reason)
            self._bus.publish(PaymentFailedEvent(e.order_id, reason))
