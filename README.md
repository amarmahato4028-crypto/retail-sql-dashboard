# Retail SQL Analytics Dashboard

A full data pipeline + analytics dashboard: synthetic retail data → normalized
SQLite database → SQL queries (joins, CTEs, window functions) → an
interactive Streamlit dashboard you can deploy live for free.

**Live demo:** _add your deployed link here once you finish the deploy step below_

---

## Why this project

Most junior portfolios have a to-do app and stop there. This project is
built to demonstrate the things interviewers actually screen for at the
entry level:

- **Database design** — a properly normalized schema instead of one flat table
- **Real SQL** — not just `SELECT *`, but joins, `GROUP BY`, Common Table
  Expressions (CTEs), and window functions (`RANK()`, `LAG()`, `SUM() OVER()`)
- **A working end-to-end pipeline** — data generation → loading → querying → visualization
- **Something deployed and clickable**, not just code sitting in a repo

---

## How it's built (the concepts, explained)

### 1. The data — `generate_data.py`
Instead of downloading a dataset (which makes the project depend on an
external file existing forever), the script **generates** realistic retail
data: 200 customers, 18 products across 4 categories, 900 orders, and their
line items. `random.seed(42)` makes the data reproducible — running it
twice gives identical output, which matters when you're debugging.

### 2. The schema — `schema.sql`
This is the most important file to be able to *explain in an interview*.
The database has four tables:

```
customers ──< orders ──< order_items >── products
```

- `customers` and `products` each hold one kind of entity.
- `orders` holds one row per order, linked to the customer who placed it.
- `order_items` is a **junction table**: an order can have many products,
  and a product appears in many orders (a many-to-many relationship),
  so it needs its own table with a foreign key to each side.
- `unit_price` is duplicated onto `order_items` *on purpose* — it freezes
  the price at the moment of purchase. If you only looked up the price
  from `products`, a price change later would silently rewrite history.

This is called **3rd Normal Form (3NF)**: every non-key column depends on
the whole primary key and nothing but the key. It's the standard your SQL
questions in interviews will assume.

### 3. Loading — `load_data.py`
A tiny ETL (Extract, Transform, Load) script: reads the CSVs with pandas,
builds the schema, and writes the rows into `retail.db` (a single-file
SQLite database — no server to install, perfect for a portfolio project).

### 4. The queries — `queries.sql`
Seven queries, each demonstrating a specific SQL skill:

| # | Query | Skill shown |
|---|-------|-------------|
| 1 | Monthly revenue | JOIN + GROUP BY + date functions |
| 2 | Top 5 products | JOIN + aggregation + ORDER BY/LIMIT |
| 3 | Revenue % by category | **CTE** + window function `SUM() OVER()` |
| 4 | Customer lifetime value ranking | window function `RANK()` |
| 5 | Month-over-month growth | window function `LAG()` |
| 6 | Order status breakdown | simple GROUP BY |
| 7 | Repeat customer count | subquery + HAVING |

**Why window functions matter:** a normal `GROUP BY` collapses rows. A
window function (`... OVER (...)`) lets you calculate something *across*
a group of rows (like a running rank or the previous month's value)
**without** collapsing them — you keep every row and add a calculated
column. This is one of the most commonly tested SQL skills in technical
interviews and a lot of bootcamp grads never touch it, so it's worth
highlighting on your resume.

### 5. The dashboard — `app.py`
[Streamlit](https://streamlit.io) turns a plain Python script into a web
app — no HTML/CSS/JS needed. Each `st.something(...)` call renders a
widget. The app runs the same SQL from `queries.sql`, loads results into
pandas DataFrames, and displays them as metrics, tables, and charts.

---

## Running it locally

```bash
# 1. Clone your repo and enter it
git clone https://github.com/YOUR-USERNAME/retail-sql-dashboard.git
cd retail-sql-dashboard

# 2. Create a virtual environment (keeps dependencies isolated)
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate the data and build the database
python generate_data.py
python load_data.py

# 5. Launch the dashboard
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`.

---

## Pushing this to GitHub

```bash
cd retail-sql-dashboard
git init
git add .
git commit -m "Initial commit: retail SQL analytics dashboard"
```

Then on github.com: click **New repository**, name it
`retail-sql-dashboard`, leave it empty (no README/license — you already
have one), and create it. GitHub will show you the remote URL — run:

```bash
git remote add origin https://github.com/YOUR-USERNAME/retail-sql-dashboard.git
git branch -M main
git push -u origin main
```

Refresh the GitHub page and your files should be there.

---

## Deploying it live (free, no server needed)

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in
   with your GitHub account.
2. Click **New app**.
3. Pick your `retail-sql-dashboard` repo, branch `main`, and main file
   path `app.py`.
4. Click **Deploy**.

Streamlit Cloud installs everything from `requirements.txt` and runs
`app.py`. The first load will take a few seconds while it generates the
database (see the `if not os.path.exists(DB_PATH)` block in `app.py`) —
after that it's cached and instant.

You'll get a URL like `https://your-app-name.streamlit.app` — put that at
the top of this README and on your resume/LinkedIn as a live link.

---

## Ideas to extend it (good for a "v2" commit / interview talking point)

- Add a date-range filter in the sidebar (`st.sidebar.date_input`)
- Add a category filter (`st.selectbox`)
- Swap SQLite for Postgres (e.g. via Supabase's free tier) to show you
  can work with a client-server database, not just a file-based one
- Add a `tests/` folder with `pytest` tests that check the queries return
  the expected columns and row counts
- Add a `.github/workflows/test.yml` GitHub Action that runs the tests
  on every push (shows CI/CD awareness)

## Project structure

```
retail-sql-dashboard/
├── app.py              # Streamlit dashboard (the deployed app)
├── generate_data.py    # Creates synthetic CSV data
├── load_data.py        # Loads CSVs into SQLite following schema.sql
├── schema.sql           # Database schema (normalized, 3NF)
├── queries.sql          # Standalone analytical queries, documented
├── requirements.txt     # Python dependencies
├── data/                 # Generated CSVs (created by generate_data.py)
└── README.md
```
