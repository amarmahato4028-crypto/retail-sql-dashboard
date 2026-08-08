-- queries.sql
-- Analytical queries against retail.db. Each one is commented with what
-- it does and why it's a useful skill to show on a resume/interview.
-- These are the same queries the Streamlit dashboard runs (see app.py).

-- 1) TOTAL REVENUE PER MONTH
-- Basic JOIN + GROUP BY + date truncation. Only counts completed orders.
SELECT
    strftime('%Y-%m', o.order_date) AS month,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY month
ORDER BY month;

-- 2) TOP 5 PRODUCTS BY REVENUE
SELECT
    p.product_name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.status = 'completed'
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 5;

-- 3) REVENUE BY CATEGORY, WITH % OF TOTAL (CTE + window function)
-- The CTE (category_revenue) computes revenue per category first.
-- The outer query uses SUM() OVER () — a window function — to get the
-- grand total *without collapsing rows*, so we can compute a percentage
-- per row while still seeing every category.
WITH category_revenue AS (
    SELECT
        p.category,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.status = 'completed'
    GROUP BY p.category
)
SELECT
    category,
    ROUND(revenue, 2) AS revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 1) AS pct_of_total
FROM category_revenue
ORDER BY revenue DESC;

-- 4) CUSTOMER LIFETIME VALUE + RANK (window function: RANK())
-- RANK() OVER (ORDER BY ... DESC) numbers customers by total spend,
-- which is far more efficient than a subquery-per-row approach.
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS lifetime_value,
    RANK() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS spend_rank
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY c.customer_id
ORDER BY spend_rank
LIMIT 10;

-- 5) MONTH-OVER-MONTH REVENUE GROWTH (window function: LAG())
-- LAG() looks at the *previous row's* value within the ordered result,
-- letting us compute growth without a self-join.
WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS month,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY month
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(revenue - LAG(revenue) OVER (ORDER BY month), 2) AS change_vs_prev_month,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
          / LAG(revenue) OVER (ORDER BY month), 1) AS pct_change
FROM monthly_revenue
ORDER BY month;

-- 6) ORDER STATUS BREAKDOWN
SELECT status, COUNT(*) AS order_count
FROM orders
GROUP BY status
ORDER BY order_count DESC;

-- 7) REPEAT CUSTOMERS (customers with more than 1 completed order)
SELECT
    COUNT(*) AS repeat_customers
FROM (
    SELECT customer_id
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
    HAVING COUNT(*) > 1
);
