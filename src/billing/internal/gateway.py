class FakePaymentGateway:
    """Имитация платёжного шлюза: отклоняет суммы выше лимита."""
    def __init__(self, limit_cents: int = 200_000) -> None:
        self.limit_cents = limit_cents

    def charge(self, amount_cents: int):
        if amount_cents > self.limit_cents:
            return False, "Превышен лимит по карте"
        return True, None
