"""Load generated CSVs into a SQLite database."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Callable, Iterable, List, Sequence


DATA_DIR = Path("data")
DB_PATH = Path("ecom.db")


def get_connection(db_path: Path) -> sqlite3.Connection:
    """Create a SQLite connection with foreign keys enforced."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def reset_database(db_path: Path) -> None:
    """Remove any existing DB so we start clean."""
    if db_path.exists():
        db_path.unlink()


def create_tables(conn: sqlite3.Connection) -> None:
    """Create tables with types and foreign key relationships."""
    conn.executescript(
        """
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            email       TEXT NOT NULL,
            country     TEXT,
            created_at  TEXT
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name       TEXT NOT NULL,
            category   TEXT,
            price      REAL NOT NULL
        );

        CREATE TABLE orders (
            order_id    INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date  TEXT NOT NULL,
            status      TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        );

        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id      INTEGER NOT NULL,
            product_id    INTEGER NOT NULL,
            quantity      INTEGER NOT NULL,
            unit_price    REAL NOT NULL,
            FOREIGN KEY (order_id)   REFERENCES orders (order_id)   ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        );

        CREATE TABLE payments (
            payment_id     INTEGER PRIMARY KEY,
            order_id       INTEGER NOT NULL,
            amount         REAL NOT NULL,
            payment_method TEXT NOT NULL,
            payment_date   TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()


def _insert_rows(
    conn: sqlite3.Connection,
    table: str,
    columns: Sequence[str],
    rows: Iterable[Sequence[object]],
) -> None:
    placeholders = ",".join("?" for _ in columns)
    sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
    conn.executemany(sql, rows)
    conn.commit()


def load_csv(
    conn: sqlite3.Connection,
    csv_path: Path,
    table: str,
    columns: Sequence[str],
    converters: Sequence[Callable[[str], object]],
) -> None:
    """Load a CSV file into a table, applying type converters column-wise."""
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        prepared_rows: List[List[object]] = []
        for raw in reader:
            prepared_rows.append(
                [
                    converter(raw[column])
                    for column, converter in zip(columns, converters)
                ]
            )
    _insert_rows(conn, table, columns, prepared_rows)


def main() -> None:
    reset_database(DB_PATH)
    conn = get_connection(DB_PATH)
    create_tables(conn)

    load_csv(
        conn,
        DATA_DIR / "customers.csv",
        "customers",
        ["customer_id", "name", "email", "country", "created_at"],
        [int, str, str, str, str],
    )
    load_csv(
        conn,
        DATA_DIR / "products.csv",
        "products",
        ["product_id", "name", "category", "price"],
        [int, str, str, float],
    )
    load_csv(
        conn,
        DATA_DIR / "orders.csv",
        "orders",
        ["order_id", "customer_id", "order_date", "status"],
        [int, int, str, str],
    )
    load_csv(
        conn,
        DATA_DIR / "order_items.csv",
        "order_items",
        ["order_item_id", "order_id", "product_id", "quantity", "unit_price"],
        [int, int, int, int, float],
    )
    load_csv(
        conn,
        DATA_DIR / "payments.csv",
        "payments",
        ["payment_id", "order_id", "amount", "payment_method", "payment_date"],
        [int, int, float, str, str],
    )

    conn.close()
    print(f"Loaded CSVs into {DB_PATH.resolve()}")


if __name__ == "__main__":
    main()

