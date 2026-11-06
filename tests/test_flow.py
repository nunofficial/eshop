import unittest
from src.app import build_app
from src.shared_kernel import InsufficientStockError, NotFoundError

class FlowTests(unittest.TestCase):
    def setUp(self):
        self.app = build_app()
        self.u = self.app.users.register("a@b.c", "A")
        self.p = self.app.catalog.add_product("Мышь", 2_500, 10)
        self.big = self.app.catalog.add_product("Ноутбук", 150_000, 3)

    def test_paid_order(self):
        self.app.orders.add_to_cart(self.u.id, self.p.id, 2)
        o = self.app.orders.checkout(self.u.id)
        self.assertEqual(self.app.orders.get_order(o.id).status, "PAID")
        self.assertEqual(self.app.billing.get_invoice_by_order(o.id).status, "PAID")
        self.assertEqual(self.app.catalog.get_product(self.p.id).stock, 8)

    def test_failed_payment_cancels_and_releases_stock(self):
        self.app.orders.add_to_cart(self.u.id, self.big.id, 2)
        o = self.app.orders.checkout(self.u.id)
        self.assertEqual(self.app.orders.get_order(o.id).status, "CANCELLED")
        self.assertEqual(self.app.billing.get_invoice_by_order(o.id).status, "FAILED")
        self.assertEqual(self.app.catalog.get_product(self.big.id).stock, 3)

    def test_insufficient_stock_rolls_back_reservations(self):
        self.app.orders.add_to_cart(self.u.id, self.p.id, 2)
        self.app.orders.add_to_cart(self.u.id, self.big.id, 99)
        with self.assertRaises(InsufficientStockError):
            self.app.orders.checkout(self.u.id)
        self.assertEqual(self.app.catalog.get_product(self.p.id).stock, 10)

    def test_unknown_user(self):
        with self.assertRaises(NotFoundError):
            self.app.orders.add_to_cart(999, self.p.id, 1)

if __name__ == "__main__":
    unittest.main()
