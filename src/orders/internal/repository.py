import sqlite3
from typing import List, Optional, Tuple
from .models import OrderRecord, OrderItemRecord, PENDING_PAYMENT

class OrderRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._c = conn
        self._c.executescript("""
        CREATE TABLE IF NOT EXISTS cart_items(
            user_id INTEGER NOT NULL, product_id INTEGER NOT NULL, qty INTEGER NOT NULL,
            PRIMARY KEY(user_id, product_id));
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            status TEXT NOT NULL, total_cents INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS order_items(
            order_id INTEGER NOT NULL REFERENCES orders(id),
            product_id INTEGER NOT NULL, name TEXT NOT NULL,
            unit_price_cents INTEGER NOT NULL, qty INTEGER NOT NULL);
        """)
        self._c.commit()

    # --- корзина ---
    def cart_add(self, user_id: int, product_id: int, qty: int) -> None:
        self._c.execute("""INSERT INTO cart_items(user_id, product_id, qty) VALUES (?,?,?)
            ON CONFLICT(user_id, product_id) DO UPDATE SET qty = qty + excluded.qty""",
            (user_id, product_id, qty))
        self._c.commit()

    def cart_items(self, user_id: int) -> List[Tuple[int, int]]:
        rows = self._c.execute("SELECT product_id, qty FROM cart_items WHERE user_id=? ORDER BY product_id",
                               (user_id,)).fetchall()
        return [(r["product_id"], r["qty"]) for r in rows]

    def cart_clear(self, user_id: int) -> None:
        self._c.execute("DELETE FROM cart_items WHERE user_id=?", (user_id,))
        self._c.commit()

    # --- заказы ---
    def create_order(self, user_id: int, items: List[OrderItemRecord], total_cents: int) -> int:
        cur = self._c.execute("INSERT INTO orders(user_id, status, total_cents) VALUES (?,?,?)",
                              (user_id, PENDING_PAYMENT, total_cents))
        oid = cur.lastrowid
        self._c.executemany(
            "INSERT INTO order_items(order_id, product_id, name, unit_price_cents, qty) VALUES (?,?,?,?,?)",
            [(oid, i.product_id, i.name, i.unit_price_cents, i.qty) for i in items])
        self._c.commit()
        return oid

    def get(self, order_id: int) -> Optional[OrderRecord]:
        r = self._c.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
        if not r:
            return None
        items = [OrderItemRecord(i["product_id"], i["name"], i["unit_price_cents"], i["qty"])
                 for i in self._c.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,))]
        return OrderRecord(r["id"], r["user_id"], r["status"], r["total_cents"], items)

    def set_status(self, order_id: int, status: str) -> None:
        self._c.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        self._c.commit()
