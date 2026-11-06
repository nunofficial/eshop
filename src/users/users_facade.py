from dataclasses import dataclass
from src.shared_kernel import connect, NotFoundError, ValidationError
from .internal.repository import UserRepository

@dataclass(frozen=True)
class UserDTO:
    id: int
    email: str
    name: str

class UsersFacade:
    """Публичный API модуля Users."""
    def __init__(self, db_path: str = ":memory:") -> None:
        self._repo = UserRepository(connect(db_path))

    def register(self, email: str, name: str) -> UserDTO:
        if "@" not in email or not name.strip():
            raise ValidationError("Некорректные email или имя")
        if self._repo.get_by_email(email):
            raise ValidationError("Пользователь с таким email уже существует")
        u = self._repo.add(email, name.strip())
        return UserDTO(u.id, u.email, u.name)

    def get_user(self, user_id: int) -> UserDTO:
        u = self._repo.get(user_id)
        if not u:
            raise NotFoundError(f"Пользователь {user_id} не найден")
        return UserDTO(u.id, u.email, u.name)

    def exists(self, user_id: int) -> bool:
        return self._repo.get(user_id) is not None
