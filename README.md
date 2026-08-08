# Retail SQL Analytics Dashboard

A SQL analytics project built around a synthetic retail dataset — customers, products, orders — modeled in a normalized SQLite database and explored through a Streamlit dashboard.

**Live app:** https://retail-sql-dashboard-gqv5be6t4ecarapp8fvzxi4.streamlit.app/

## What this is

I wanted a project that actually shows SQL skill, not just `SELECT * FROM table`. So instead of a flat spreadsheet-style table, this uses a proper relational schema (customers, products, orders, order_items) and runs analytical queries on top of it — joins, CTEs, and window functions like `RANK()` and `LAG()`. The dashboard on top of it is just a way to make the results visible and interactive instead of sitting in a terminal.

## Schema

```
customers ──< orders ──< order_items >── products
```

- `customers` and `products` are standalone entity tables.
- `orders` is one row per order, tied to a customer.
- `order_items` handles the many-to-many between orders and products — one order can have several products, one product shows up across many orders.
- `unit_price` is stored on `order_items`, not just looked up from `products`, so historical orders keep the price that was actually charged even if the product's price changes later.

This is 3NF (third normal form) — standard relational design, and the kind of thing that comes up in SQL interview questions.

## Queries (`queries.sql`)

| Query | What it shows |
|---|---|
| Monthly revenue | JOIN + GROUP BY + date grouping |
| Top 5 products | aggregation + ORDER BY/LIMIT |
| Revenue % by category | CTE + `SUM() OVER()` |
| Customer lifetime value ranking | `RANK()` |
| Month-over-month growth | `LAG()` |
| Order status breakdown | GROUP BY |
| Repeat customers | subquery + HAVING |

Window functions specifically are worth calling out — they let you compute something across a set of rows (a rank, a running total, the previous row's value) without collapsing the result the way `GROUP BY` does. It's a step past basic SQL that a lot of intro projects skip.

## Stack

- **SQLite** — single-file database, no server setup
- **pandas** — reads CSVs, loads them into SQLite
- **Streamlit** — turns the queries into an interactive dashboard, no frontend code

## Running it locally

```
git clone https://github.com/amarmahato4028-crypto/retail-sql-dashboard.git
cd retail-sql-dashboard
pip install -r requirements.txt
python generate_data.py
python load_data.py
streamlit run app.py
```

## Project structure

```
retail-sql-dashboard/
├── app.py             # dashboard
├── generate_data.py   # generates the synthetic dataset
├── load_data.py       # loads CSVs into SQLite
├── schema.sql          # table definitions
├── queries.sql          # the analytical queries, documented
├── requirements.txt
├── data/                 # generated CSVs
└── retail.db              # the built database
```

## What I'd add next

- Date range and category filters on the dashboard
- Move from SQLite to Postgres to work with a client-server DB
- Basic tests on the query outputs
