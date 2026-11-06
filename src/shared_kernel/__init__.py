"""SharedKernel: только общие примитивы (ошибки, Money, шина событий, контракты событий).
Никакой бизнес-логики и никаких сущностей БД."""
from .errors import DomainError, NotFoundError, ValidationError, InsufficientStockError
from .money import Money
from .events import DomainEvent, EventBus
from .contracts import OrderCreatedEvent, PaymentSucceededEvent, PaymentFailedEvent
from .db import connect
