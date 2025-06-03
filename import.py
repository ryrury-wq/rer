import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# === НАСТРОЙКИ ===
SQLITE_PATH = "expiry.db"  # Локальный файл
POSTGRES_URL = "postgresql://user:pass@host:port/dbname"  # <-- ВСТАВЬ СЮДА URL с Render

# === ЧТЕНИЕ SQLite ===
conn = sqlite3.connect(SQLITE_PATH)
products_df = pd.read_sql_query("SELECT * FROM products", conn)
batches_df = pd.read_sql_query("SELECT * FROM batches", conn)
history_df = pd.read_sql_query("SELECT * FROM history", conn)
conn.close()

# === СОЕДИНЕНИЕ С PostgreSQL ===
engine = create_engine(POSTGRES_URL)

# === СОЗДАНИЕ ТАБЛИЦ (если нужно вручную — выключи этот блок) ===
with engine.connect() as connection:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            barcode TEXT,
            name TEXT
        );
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(id),
            expiration_date DATE,
            added_date DATE DEFAULT CURRENT_DATE
        );
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id SERIAL PRIMARY KEY,
            barcode TEXT,
            product_name TEXT,
            expiration_date DATE,
            removed_date DATE DEFAULT CURRENT_DATE
        );
    """)

# === ИМПОРТ В PostgreSQL ===
products_df.to_sql("products", engine, if_exists="append", index=False)
batches_df.to_sql("batches", engine, if_exists="append", index=False)
history_df.to_sql("history", engine, if_exists="append", index=False)

print("Импорт завершён успешно.")
