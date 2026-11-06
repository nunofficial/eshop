class DomainError(Exception):
    """Базовая ошибка предметной области."""

class NotFoundError(DomainError):
    pass

class ValidationError(DomainError):
    pass

class InsufficientStockError(DomainError):
    pass
