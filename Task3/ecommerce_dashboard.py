import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Load CSVs
df_customers = pd.read_csv("ecommerce_customers.csv")
df_orders = pd.read_csv("ecommerce_orders.csv")

# Connect to SQLite DB
conn = sqlite3.connect("ecommerce.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    country TEXT
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    amount REAL,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);
""")

# Insert data
df_customers.to_sql("customers", conn, if_exists="replace", index=False)
df_orders.to_sql("orders", conn, if_exists="replace", index=False)

# Streamlit App
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")
st.title("E-commerce SQL Data Analysis Dashboard")

# Total Revenue
revenue_query = "SELECT SUM(amount) AS total_revenue FROM orders;"
total_revenue = pd.read_sql_query(revenue_query, conn).iloc[0, 0]
st.metric("Total Revenue", f"${total_revenue:,.2f}")

# Orders by Country
country_query = """
SELECT c.country, COUNT(o.id) as num_orders
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.country;
"""
df_country_orders = pd.read_sql_query(country_query, conn)
st.subheader("Orders by Country")
st.bar_chart(df_country_orders.set_index("country"))

# Top Customers
top_customers_query = """
SELECT c.name, SUM(o.amount) as total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.name
ORDER BY total_spent DESC
LIMIT 5;
"""
df_top_customers = pd.read_sql_query(top_customers_query, conn)
st.subheader("Top 5 Customers by Spending")
st.dataframe(df_top_customers)

conn.close()
