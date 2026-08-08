"""
load_data.py
------------
Builds retail.db (SQLite) from schema.sql, then loads the CSVs from data/
into the tables. This is a tiny "ETL": Extract (read CSVs) -> Transform
(pandas handles type parsing) -> Load (write to SQLite).

Run: python load_data.py
Output: retail.db
"""

import sqlite3
import pandas as pd

DB_PATH = "retail.db"

def build_schema(conn):
    with open("schema.sql") as f:
        conn.executescript(f.read())

def load_table(conn, csv_path, table_name):
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into {table_name}")

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    build_schema(conn)

    load_table(conn, "data/customers.csv", "customers")
    load_table(conn, "data/products.csv", "products")
    load_table(conn, "data/orders.csv", "orders")
    load_table(conn, "data/order_items.csv", "order_items")

    conn.commit()
    conn.close()
    print(f"\nDatabase ready: {DB_PATH}")
