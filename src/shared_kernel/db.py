import sqlite3

def connect(path: str = ":memory:") -> sqlite3.Connection:
    """Создаёт ОТДЕЛЬНОЕ соединение. Каждый модуль вызывает это сам и получает
    собственную БД (для ':memory:' — физически изолированную)."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn
