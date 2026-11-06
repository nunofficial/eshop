from dataclasses import dataclass
from typing import List, Optional
from src.shared_kernel import connect, NotFoundError, ValidationError, InsufficientStockError
from .internal.repository import CatalogRepository

@dataclass(frozen=True)
class ProductDTO:
    id: int
    name: str
    price_cents: int
    stock: int
    category_id: Optional[int]

class CatalogFacade:
    """Публичный API модуля Catalog. Наружу отдаются только DTO."""
    def __init__(self, db_path: str = ":memory:") -> None:
        self._repo = CatalogRepository(connect(db_path))

    @staticmethod
    def _dto(p) -> ProductDTO:
        return ProductDTO(p.id, p.name, p.price_cents, p.stock, p.category_id)

    def create_category(self, name: str) -> int:
        return self._repo.add_category(name)

    def add_product(self, name: str, price_cents: int, stock: int,
                    category_id: Optional[int] = None) -> ProductDTO:
        if price_cents < 0 or stock < 0 or not name.strip():
            raise ValidationError("Некорректные данные товара")
        return self._dto(self._repo.add_product(name, price_cents, stock, category_id))

    def get_product(self, product_id: int) -> ProductDTO:
        p = self._repo.get(product_id)
        if not p:
            raise NotFoundError(f"Товар {product_id} не найден")
        return self._dto(p)

    def list_products(self, category_id: Optional[int] = None) -> List[ProductDTO]:
        return [self._dto(p) for p in self._repo.list(category_id)]

    def reserve_stock(self, product_id: int, qty: int) -> None:
        if qty <= 0:
            raise ValidationError("Количество должно быть > 0")
        self.get_product(product_id)
        if not self._repo.try_reserve(product_id, qty):
            raise InsufficientStockError(f"Недостаточно товара {product_id} на складе")

    def release_stock(self, product_id: int, qty: int) -> None:
        if qty <= 0:
            raise ValidationError("Количество должно быть > 0")
        self._repo.release(product_id, qty)
