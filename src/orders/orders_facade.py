from dataclasses import dataclass
from typing import List
from src.shared_kernel import (connect, DomainError, NotFoundError, ValidationError, EventBus,
                               OrderCreatedEvent, PaymentSucceededEvent, PaymentFailedEvent)
from src.users import UsersFacade          # разрешено: Orders -> Users (только фасад)
from src.catalog import CatalogFacade      # разрешено: Orders -> Catalog (только фасад)
from .internal.models import OrderItemRecord, PENDING_PAYMENT, PAID, CANCELLED
from .internal.repository import OrderRepository

@dataclass(frozen=True)
class OrderItemDTO:
    product_id: int
    name: str
    unit_price_cents: int
    qty: int

@dataclass(frozen=True)
class OrderDTO:
    id: int
    user_id: int
    status: str
    total_cents: int
    items: List[OrderItemDTO]

class OrdersFacade:
    """Публичный API модуля Orders.
    Зависит от Users и Catalog (через их фасады) и от шины событий.
    О Billing ничего не знает: общается с ним только через события."""
    def __init__(self, users: UsersFacade, catalog: CatalogFacade, bus: EventBus,
                 db_path: str = ":memory:") -> None:
        self._users, self._catalog, self._bus = users, catalog, bus
        self._repo = OrderRepository(connect(db_path))
        bus.subscribe(PaymentSucceededEvent, self._on_payment_succeeded)
        bus.subscribe(PaymentFailedEvent, self._on_payment_failed)

    # ---- публичные методы ----
    def add_to_cart(self, user_id: int, product_id: int, qty: int) -> None:
        if qty <= 0:
            raise ValidationError("Количество должно быть > 0")
        if not self._users.exists(user_id):
            raise NotFoundError(f"Пользователь {user_id} не найден")
        self._catalog.get_product(product_id)   # бросит NotFoundError, если товара нет
        self._repo.cart_add(user_id, product_id, qty)

    def checkout(self, user_id: int) -> OrderDTO:
        self._users.get_user(user_id)
        cart = self._repo.cart_items(user_id)
        if not cart:
            raise ValidationError("Корзина пуста")
        reserved, lines = [], []
        try:
            for product_id, qty in cart:
                p = self._catalog.get_product(product_id)
                self._catalog.reserve_stock(product_id, qty)
                reserved.append((product_id, qty))
                lines.append(OrderItemRecord(product_id, p.name, p.price_cents, qty))
        except DomainError:
            for pid, q in reserved:             # компенсация: вернуть уже зарезервированное
                self._catalog.release_stock(pid, q)
            raise
        total = sum(l.unit_price_cents * l.qty for l in lines)
        order_id = self._repo.create_order(user_id, lines, total)
        self._repo.cart_clear(user_id)
        self._bus.publish(OrderCreatedEvent(order_id, user_id, total))
        return self.get_order(order_id)

    def get_order(self, order_id: int) -> OrderDTO:
        o = self._repo.get(order_id)
        if not o:
            raise NotFoundError(f"Заказ {order_id} не найден")
        return OrderDTO(o.id, o.user_id, o.status, o.total_cents,
                        [OrderItemDTO(i.product_id, i.name, i.unit_price_cents, i.qty) for i in o.items])

    # ---- обработчики событий (реакция на Billing без знания о нём) ----
    def _on_payment_succeeded(self, e: PaymentSucceededEvent) -> None:
        o = self._repo.get(e.order_id)
        if o and o.status == PENDING_PAYMENT:
            self._repo.set_status(o.id, PAID)

    def _on_payment_failed(self, e: PaymentFailedEvent) -> None:
        o = self._repo.get(e.order_id)
        if o and o.status == PENDING_PAYMENT:
            for i in o.items:
                self._catalog.release_stock(i.product_id, i.qty)
            self._repo.set_status(o.id, CANCELLED)
