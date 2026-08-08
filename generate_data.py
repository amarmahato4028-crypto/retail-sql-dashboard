"""
generate_data.py
-----------------
Creates a synthetic but realistic retail dataset and writes it to CSV files
in the data/ folder. We generate our own data (instead of downloading a
public dataset) so the project has no external dependency and works
offline — but the shape of the data (customers, products, orders,
order_items) mirrors a real e-commerce database.

Run: python generate_data.py
Output: data/customers.csv, data/products.csv, data/orders.csv, data/order_items.csv
"""

import csv
import random
from datetime import date, timedelta

random.seed(42)  # reproducible data — same output every run

FIRST_NAMES = ["Amar", "Priya", "James", "Maria", "Wei", "Fatima", "Liam",
               "Sofia", "Ravi", "Emma", "Noah", "Aisha", "Carlos", "Yuki",
               "Olivia", "Ethan", "Zara", "Daniel", "Mei", "Lucas"]
LAST_NAMES = ["Kumar", "Smith", "Garcia", "Chen", "Patel", "Johnson", "Khan",
              "Rossi", "Silva", "Nguyen", "Brown", "Ali", "Kim", "Davis",
              "Singh", "Martin", "Lopez", "Wang", "Taylor", "Mahato"]
CITIES = [("High Point", "NC"), ("Charlotte", "NC"), ("Raleigh", "NC"),
          ("Atlanta", "GA"), ("Austin", "TX"), ("Denver", "CO"),
          ("Seattle", "WA"), ("Chicago", "IL"), ("Boston", "MA"),
          ("Phoenix", "AZ")]

CATEGORIES = {
    "Electronics": [("Wireless Mouse", 19.99), ("Mechanical Keyboard", 74.99),
                     ("USB-C Hub", 29.99), ("Webcam 1080p", 39.99),
                     ("Bluetooth Speaker", 49.99), ("Laptop Stand", 34.99)],
    "Home & Kitchen": [("French Press", 24.99), ("Air Fryer", 89.99),
                        ("Cutting Board Set", 21.99), ("Electric Kettle", 27.99)],
    "Office Supplies": [("Notebook 3-Pack", 9.99), ("Desk Organizer", 14.99),
                         ("Ergonomic Chair", 149.99), ("Standing Desk", 219.99)],
    "Sports & Outdoors": [("Yoga Mat", 22.99), ("Water Bottle 32oz", 12.99),
                           ("Resistance Bands", 15.99), ("Running Shorts", 18.99)],
}

N_CUSTOMERS = 200
N_ORDERS = 900
ORDER_STATUSES = ["completed", "completed", "completed", "shipped", "cancelled"]

def random_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def generate_customers():
    customers = []
    for i in range(1, N_CUSTOMERS + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        city, state = random.choice(CITIES)
        signup = random_date(date(2023, 1, 1), date(2025, 12, 31))
        customers.append({
            "customer_id": i,
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}{i}@example.com",
            "city": city,
            "state": state,
            "signup_date": signup.isoformat(),
        })
    return customers

def generate_products():
    products = []
    pid = 1
    for category, items in CATEGORIES.items():
        for name, price in items:
            products.append({
                "product_id": pid,
                "product_name": name,
                "category": category,
                "unit_price": price,
            })
            pid += 1
    return products

def generate_orders_and_items(customers, products):
    orders = []
    order_items = []
    item_id = 1
    for order_id in range(1, N_ORDERS + 1):
        customer = random.choice(customers)
        order_date = random_date(date(2024, 1, 1), date(2026, 8, 1))
        status = random.choice(ORDER_STATUSES)
        orders.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "order_date": order_date.isoformat(),
            "status": status,
        })
        # each order has 1-4 line items
        n_items = random.randint(1, 4)
        chosen_products = random.sample(products, n_items)
        for p in chosen_products:
            qty = random.randint(1, 3)
            order_items.append({
                "order_item_id": item_id,
                "order_id": order_id,
                "product_id": p["product_id"],
                "quantity": qty,
                "unit_price": p["unit_price"],  # price at time of order
            })
            item_id += 1
    return orders, order_items

def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    customers = generate_customers()
    products = generate_products()
    orders, order_items = generate_orders_and_items(customers, products)

    write_csv("data/customers.csv", customers,
               ["customer_id", "first_name", "last_name", "email", "city", "state", "signup_date"])
    write_csv("data/products.csv", products,
               ["product_id", "product_name", "category", "unit_price"])
    write_csv("data/orders.csv", orders,
               ["order_id", "customer_id", "order_date", "status"])
    write_csv("data/order_items.csv", order_items,
               ["order_item_id", "order_id", "product_id", "quantity", "unit_price"])

    print(f"Generated {len(customers)} customers, {len(products)} products, "
          f"{len(orders)} orders, {len(order_items)} order items.")
