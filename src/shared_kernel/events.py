from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Dict, List, Type

@dataclass(frozen=True)
class DomainEvent:
    """Базовый класс событий."""

class EventBus:
    """Простая синхронная in-process шина событий."""
    def __init__(self) -> None:
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in list(self._handlers[type(event)]):
            handler(event)
