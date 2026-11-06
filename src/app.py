"""Composition root: единственное место, где модули собираются вместе."""
from dataclasses import dataclass
from src.shared_kernel import EventBus
from src.users import UsersFacade
from src.catalog import CatalogFacade
from src.orders import OrdersFacade
from src.billing import BillingFacade

@dataclass
class App:
    bus: EventBus
    users: UsersFacade
    catalog: CatalogFacade
    orders: OrdersFacade
    billing: BillingFacade

def build_app() -> App:
    bus = EventBus()
    users = UsersFacade()
    catalog = CatalogFacade()
    billing = BillingFacade(bus)
    orders = OrdersFacade(users, catalog, bus)
    return App(bus, users, catalog, orders, billing)
