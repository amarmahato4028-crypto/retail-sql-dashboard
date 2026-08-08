-- schema.sql
-- Normalized (3NF) schema for the retail analytics database.
--
-- Why this design?
-- - customers, products, orders, and order_items are separate tables
--   instead of one giant flat table. This avoids repeating customer or
--   product info on every row (no update anomalies, less storage).
-- - order_items is a "junction"/line-item table because one order can
--   contain many products, and one product appears in many orders
--   (a classic many-to-many, resolved with its own table).
-- - unit_price is stored on order_items, NOT just looked up from products,
--   because prices change over time — we want to know what the customer
--   actually paid on that order, not today's price.

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id   INTEGER PRIMARY KEY,
    first_name    TEXT NOT NULL,
    last_name     TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    city          TEXT,
    state         TEXT,
    signup_date   DATE NOT NULL
);

CREATE TABLE products (
    product_id    INTEGER PRIMARY KEY,
    product_name  TEXT NOT NULL,
    category      TEXT NOT NULL,
    unit_price    NUMERIC NOT NULL
);

CREATE TABLE orders (
    order_id      INTEGER PRIMARY KEY,
    customer_id   INTEGER NOT NULL,
    order_date    DATE NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('completed', 'shipped', 'cancelled')),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id      INTEGER NOT NULL,
    product_id    INTEGER NOT NULL,
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    unit_price    NUMERIC NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Indexes on foreign keys speed up the JOINs we'll run in queries.sql
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_items_order ON order_items(order_id);
CREATE INDEX idx_items_product ON order_items(product_id);
