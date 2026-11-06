from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    """Value Object: сумма в минимальных единицах (центы), без float-ошибок."""
    cents: int

    def __str__(self) -> str:
        return f"{self.cents // 100}.{self.cents % 100:02d}"

    def __add__(self, other: "Money") -> "Money":
        return Money(self.cents + other.cents)
