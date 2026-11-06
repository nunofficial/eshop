import sqlite3
from typing import List, Optional
from .models import ProductRecord

def _row(r) -> ProductRecord:
    return ProductRecord(r["id"], r["name"], r["price_cents"], r["stock"], r["category_id"])

class CatalogRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._c = conn
        self._c.executescript("""
        CREATE TABLE IF NOT EXISTS categories(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL);
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
            stock INTEGER NOT NULL CHECK(stock >= 0),
            category_id INTEGER REFERENCES categories(id));
        """)
        self._c.commit()

    def add_category(self, name: str) -> int:
        cur = self._c.execute("INSERT INTO categories(name) VALUES (?)", (name,))
        self._c.commit()
        return cur.lastrowid

    def add_product(self, name, price_cents, stock, category_id) -> ProductRecord:
        cur = self._c.execute(
            "INSERT INTO products(name, price_cents, stock, category_id) VALUES (?,?,?,?)",
            (name, price_cents, stock, category_id))
        self._c.commit()
        return self.get(cur.lastrowid)

    def get(self, product_id: int) -> Optional[ProductRecord]:
        r = self._c.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
        return _row(r) if r else None

    def list(self, category_id: Optional[int] = None) -> List[ProductRecord]:
        if category_id is None:
            rows = self._c.execute("SELECT * FROM products ORDER BY id").fetchall()
        else:
            rows = self._c.execute("SELECT * FROM products WHERE category_id=? ORDER BY id",
                                   (category_id,)).fetchall()
        return [_row(r) for r in rows]

    def try_reserve(self, product_id: int, qty: int) -> bool:
        """Атомарное списание: срабатывает только если остатка хватает."""
        cur = self._c.execute(
            "UPDATE products SET stock = stock - ? WHERE id=? AND stock >= ?",
            (qty, product_id, qty))
        self._c.commit()
        return cur.rowcount == 1

    def release(self, product_id: int, qty: int) -> None:
        self._c.execute("UPDATE products SET stock = stock + ? WHERE id=?", (qty, product_id))
        self._c.commit()
