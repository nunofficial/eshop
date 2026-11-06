import sqlite3
from typing import Optional
from .models import InvoiceRecord, ISSUED

def _row(r) -> InvoiceRecord:
    return InvoiceRecord(r["id"], r["order_id"], r["user_id"], r["amount_cents"], r["status"], r["reason"])

class InvoiceRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._c = conn
        self._c.execute("""CREATE TABLE IF NOT EXISTS invoices(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER UNIQUE NOT NULL, user_id INTEGER NOT NULL,
            amount_cents INTEGER NOT NULL, status TEXT NOT NULL, reason TEXT)""")
        self._c.commit()

    def add(self, order_id: int, user_id: int, amount_cents: int) -> InvoiceRecord:
        cur = self._c.execute(
            "INSERT INTO invoices(order_id, user_id, amount_cents, status) VALUES (?,?,?,?)",
            (order_id, user_id, amount_cents, ISSUED))
        self._c.commit()
        return self.get(cur.lastrowid)

    def get(self, invoice_id: int) -> Optional[InvoiceRecord]:
        r = self._c.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone()
        return _row(r) if r else None

    def get_by_order(self, order_id: int) -> Optional[InvoiceRecord]:
        r = self._c.execute("SELECT * FROM invoices WHERE order_id=?", (order_id,)).fetchone()
        return _row(r) if r else None

    def set_status(self, invoice_id: int, status: str, reason: Optional[str] = None) -> None:
        self._c.execute("UPDATE invoices SET status=?, reason=? WHERE id=?", (status, reason, invoice_id))
        self._c.commit()
