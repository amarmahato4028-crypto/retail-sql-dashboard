"""
app.py
------
Streamlit dashboard for the retail analytics SQLite database.

This is the "live" part of the project — Streamlit turns this single
Python file into a web app, and Streamlit Community Cloud can host it
for free straight from your GitHub repo (see README.md for deploy steps).

Run locally: streamlit run app.py
"""

import os
import subprocess
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")

DB_PATH = "retail.db"

# If the database doesn't exist yet (e.g. first boot on Streamlit Cloud,
# where we don't commit the binary .db file to git), build it on the fly
# from the scripts. This keeps the repo small and makes the app
# self-sufficient wherever it's deployed.
if not os.path.exists(DB_PATH):
    with st.spinner("First run: generating sample data..."):
        subprocess.run(["python", "generate_data.py"], check=True)
        subprocess.run(["python", "load_data.py"], check=True)

@st.cache_resource
def get_connection():
    # check_same_thread=False is safe here because Streamlit reruns the
    # script top-to-bottom on each interaction and we only ever read.
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def run_query(conn, sql):
    return pd.read_sql_query(sql, conn)

conn = get_connection()

st.title("📊 Retail Analytics Dashboard")
st.caption("SQLite + SQL analytics + Streamlit — synthetic retail data, real query patterns.")

# ---- KPI row -----------------------------------------------------------
kpi_sql = """
SELECT
    (SELECT ROUND(SUM(oi.quantity * oi.unit_price), 2)
     FROM order_items oi JOIN orders o ON o.order_id = oi.order_id
     WHERE o.status = 'completed') AS total_revenue,
    (SELECT COUNT(*) FROM orders WHERE status = 'completed') AS completed_orders,
    (SELECT COUNT(DISTINCT customer_id) FROM orders WHERE status = 'completed') AS active_customers
"""
kpis = run_query(conn, kpi_sql).iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${kpis['total_revenue']:,.2f}")
col2.metric("Completed Orders", f"{int(kpis['completed_orders']):,}")
col3.metric("Active Customers", f"{int(kpis['active_customers']):,}")

st.divider()

# ---- Revenue by month ----------------------------------------------------
st.subheader("Monthly Revenue")
monthly_sql = """
SELECT strftime('%Y-%m', o.order_date) AS month,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY month
ORDER BY month
"""
monthly_df = run_query(conn, monthly_sql)
st.bar_chart(monthly_df.set_index("month")["revenue"])

# ---- Two-column: category split + top products --------------------------
left, right = st.columns(2)

with left:
    st.subheader("Revenue by Category")
    category_sql = """
    WITH category_revenue AS (
        SELECT p.category, SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        JOIN orders o ON o.order_id = oi.order_id
        WHERE o.status = 'completed'
        GROUP BY p.category
    )
    SELECT category, ROUND(revenue, 2) AS revenue,
           ROUND(100.0 * revenue / SUM(revenue) OVER (), 1) AS pct_of_total
    FROM category_revenue
    ORDER BY revenue DESC
    """
    category_df = run_query(conn, category_sql)
    st.dataframe(category_df, hide_index=True, use_container_width=True)

with right:
    st.subheader("Top 5 Products")
    top_products_sql = """
    SELECT p.product_name, p.category,
           SUM(oi.quantity) AS units_sold,
           ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.status = 'completed'
    GROUP BY p.product_id
    ORDER BY revenue DESC
    LIMIT 5
    """
    top_products_df = run_query(conn, top_products_sql)
    st.dataframe(top_products_df, hide_index=True, use_container_width=True)

st.divider()

# ---- Top customers (window function: RANK) ------------------------------
st.subheader("Top 10 Customers by Lifetime Value")
top_customers_sql = """
SELECT c.first_name || ' ' || c.last_name AS customer_name,
       c.city, c.state,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS lifetime_value,
       RANK() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS spend_rank
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY c.customer_id
ORDER BY spend_rank
LIMIT 10
"""
top_customers_df = run_query(conn, top_customers_sql)
st.dataframe(top_customers_df, hide_index=True, use_container_width=True)

# ---- Order status breakdown ---------------------------------------------
st.subheader("Order Status Breakdown")
status_sql = "SELECT status, COUNT(*) AS order_count FROM orders GROUP BY status ORDER BY order_count DESC"
status_df = run_query(conn, status_sql)
st.bar_chart(status_df.set_index("status")["order_count"])

st.divider()
st.caption("Built with Python, SQLite, and Streamlit. Data is synthetic (generated by generate_data.py).")
