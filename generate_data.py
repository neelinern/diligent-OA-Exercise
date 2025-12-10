"""
Synthetic e-commerce data generator.

Outputs five CSV tables under ./data:
- customers
- products
- orders
- order_items
- payments

If you do not have Faker installed, install it with:
    pip install faker
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

try:
    from faker import Faker
except ImportError as exc:  # pragma: no cover - guidance for user
    raise SystemExit(
        "Faker is required. Install it with: pip install faker"
    ) from exc


DATA_DIR = Path("data")
NUM_CUSTOMERS = 100
NUM_PRODUCTS = 50
NUM_ORDERS = 300
MAX_ITEMS_PER_ORDER = 5


fake = Faker()
random.seed()


@dataclass
class Customer:
    customer_id: int
    name: str
    email: str
    country: str
    created_at: str


@dataclass
class Product:
    product_id: int
    name: str
    category: str
    price: float


@dataclass
class Order:
    order_id: int
    customer_id: int
    order_date: str
    status: str


@dataclass
class OrderItem:
    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float


@dataclass
class Payment:
    payment_id: int
    order_id: int
    amount: float
    payment_method: str
    payment_date: str


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(exist_ok=True)


def generate_customers(count: int) -> List[Customer]:
    customers: List[Customer] = []
    for idx in range(1, count + 1):
        created_at = fake.date_time_between(start_date="-2y", end_date="now")
        customers.append(
            Customer(
                customer_id=idx,
                name=fake.name(),
                email=fake.unique.email(),
                country=fake.country(),
                created_at=created_at.isoformat(sep=" ", timespec="seconds"),
            )
        )
    return customers


def generate_products(count: int) -> List[Product]:
    categories = [
        "Electronics",
        "Home",
        "Clothing",
        "Sports",
        "Books",
        "Toys",
        "Grocery",
        "Beauty",
    ]
    products: List[Product] = []
    for idx in range(1, count + 1):
        category = random.choice(categories)
        name = f"{fake.word().capitalize()} {category[:-1] if category.endswith('s') else category}"
        price = round(random.uniform(5.0, 500.0), 2)
        products.append(
            Product(
                product_id=idx,
                name=name,
                category=category,
                price=price,
            )
        )
    return products


def generate_orders(count: int, customers: List[Customer]) -> List[Order]:
    statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    orders: List[Order] = []
    now = datetime.utcnow()
    for idx in range(1, count + 1):
        customer = random.choice(customers)
        order_date = now - timedelta(days=random.randint(0, 365))
        status = random.choices(
            population=statuses,
            weights=[0.15, 0.2, 0.25, 0.35, 0.05],
            k=1,
        )[0]
        orders.append(
            Order(
                order_id=idx,
                customer_id=customer.customer_id,
                order_date=order_date.isoformat(sep=" ", timespec="seconds"),
                status=status,
            )
        )
    return orders


def generate_order_items(
    orders: List[Order],
    products: List[Product],
    max_items_per_order: int,
) -> List[OrderItem]:
    order_items: List[OrderItem] = []
    order_item_id = 1
    product_lookup: Dict[int, Product] = {p.product_id: p for p in products}
    for order in orders:
        num_items = random.randint(1, max_items_per_order)
        chosen_products = random.sample(products, k=min(num_items, len(products)))
        for product in chosen_products:
            quantity = random.randint(1, 3)
            unit_price = product_lookup[product.product_id].price
            order_items.append(
                OrderItem(
                    order_item_id=order_item_id,
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=quantity,
                    unit_price=unit_price,
                )
            )
            order_item_id += 1
    return order_items


def generate_payments(orders: List[Order], order_items: List[OrderItem]) -> List[Payment]:
    payment_methods = ["card", "paypal", "bank_transfer", "gift_card"]
    payments: List[Payment] = []
    payment_id = 1

    items_by_order: Dict[int, List[OrderItem]] = {}
    for item in order_items:
        items_by_order.setdefault(item.order_id, []).append(item)

    for order in orders:
        items = items_by_order.get(order.order_id, [])
        total = sum(item.quantity * item.unit_price for item in items)
        if total == 0:
            continue
        payment_date = datetime.fromisoformat(order.order_date) + timedelta(
            days=random.randint(0, 5)
        )
        payments.append(
            Payment(
                payment_id=payment_id,
                order_id=order.order_id,
                amount=round(total, 2),
                payment_method=random.choice(payment_methods),
                payment_date=payment_date.isoformat(sep=" ", timespec="seconds"),
            )
        )
        payment_id += 1
    return payments


def write_csv(path: Path, rows: List[dataclass], headers: List[str]) -> None:
    with path.open(mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def main() -> None:
    ensure_data_dir()

    customers = generate_customers(NUM_CUSTOMERS)
    products = generate_products(NUM_PRODUCTS)
    orders = generate_orders(NUM_ORDERS, customers)
    order_items = generate_order_items(orders, products, MAX_ITEMS_PER_ORDER)
    payments = generate_payments(orders, order_items)

    write_csv(
        DATA_DIR / "customers.csv",
        customers,
        ["customer_id", "name", "email", "country", "created_at"],
    )
    write_csv(
        DATA_DIR / "products.csv",
        products,
        ["product_id", "name", "category", "price"],
    )
    write_csv(
        DATA_DIR / "orders.csv",
        orders,
        ["order_id", "customer_id", "order_date", "status"],
    )
    write_csv(
        DATA_DIR / "order_items.csv",
        order_items,
        ["order_item_id", "order_id", "product_id", "quantity", "unit_price"],
    )
    write_csv(
        DATA_DIR / "payments.csv",
        payments,
        ["payment_id", "order_id", "amount", "payment_method", "payment_date"],
    )

    print(f"Generated data in {DATA_DIR.resolve()}")


if __name__ == "__main__":
    main()

