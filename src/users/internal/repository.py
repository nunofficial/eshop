import sqlite3
from typing import Optional
from .models import UserRecord

class UserRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._c = conn
        self._c.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL)""")
        self._c.commit()

    def add(self, email: str, name: str) -> UserRecord:
        cur = self._c.execute("INSERT INTO users(email, name) VALUES (?, ?)", (email, name))
        self._c.commit()
        return UserRecord(cur.lastrowid, email, name)

    def get(self, user_id: int) -> Optional[UserRecord]:
        r = self._c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return UserRecord(r["id"], r["email"], r["name"]) if r else None

    def get_by_email(self, email: str) -> Optional[UserRecord]:
        r = self._c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        return UserRecord(r["id"], r["email"], r["name"]) if r else None
