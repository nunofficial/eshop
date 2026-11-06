from src.app import build_app
from src.shared_kernel import Money, DomainError

def main() -> None:
    app = build_app()
    user = app.users.register("kudai@example.com", "Kudai")
    cat = app.catalog.create_category("Электроника")
    mouse = app.catalog.add_product("Мышь", 2_500, stock=10, category_id=cat)
    laptop = app.catalog.add_product("Ноутбук", 150_000, stock=3, category_id=cat)

    print("== Сценарий 1: успешный заказ ==")
    app.orders.add_to_cart(user.id, mouse.id, 2)
    o1 = app.orders.checkout(user.id)
    print(f"Заказ #{o1.id}: {o1.status}, сумма {Money(o1.total_cents)}")
    print("Счёт:", app.billing.get_invoice_by_order(o1.id).status)

    print("\n== Сценарий 2: оплата отклонена -> заказ отменён, остаток возвращён ==")
    app.orders.add_to_cart(user.id, laptop.id, 2)
    o2 = app.orders.checkout(user.id)
    print(f"Заказ #{o2.id}: {app.orders.get_order(o2.id).status}")
    inv = app.billing.get_invoice_by_order(o2.id)
    print(f"Счёт: {inv.status} ({inv.reason})")
    print("Остаток ноутбуков:", app.catalog.get_product(laptop.id).stock, "(было 3)")

    print("\n== Сценарий 3: нет на складе ==")
    app.orders.add_to_cart(user.id, laptop.id, 99)
    try:
        app.orders.checkout(user.id)
    except DomainError as e:
        print("Ошибка:", e)

if __name__ == "__main__":
    main()
