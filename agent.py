import sqlite3
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
import streamlit as st
import pandas as pd 

# ── 1. Create a sample SQLite database ───────────────
conn = sqlite3.connect("sales.db")
conn.executescript("""
CREATE TABLE IF NOT EXISTS orders (
    id        INTEGER PRIMARY KEY,
    customer  TEXT NOT NULL,
    product   TEXT NOT NULL,
    amount    REAL NOT NULL,
    date      TEXT NOT NULL,
    status    TEXT DEFAULT 'delivered'
);
CREATE TABLE IF NOT EXISTS products (
    name      TEXT PRIMARY KEY,
    category  TEXT,
    stock     INTEGER,
    price     REAL
);
""")
conn.executemany("INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?,?)", [
    (1, "Rahul Sharma",   "Laptop", 75000, "2024-01-05", "delivered"),
    (2, "Priya Mehta",    "Phone",  25000, "2024-01-12", "delivered"),
    (3, "Arjun Nair",     "Tablet", 35000, "2024-01-18", "returned"),
    (4, "Rahul Sharma",   "Mouse",   1500, "2024-01-20", "delivered"),
    (5, "Divya Krishnan", "Laptop", 72000, "2024-01-22", "delivered"),
    (6, "Vikram Rao",     "Phone",  22000, "2024-01-28", "delivered"),
])
conn.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?)", [
    ("Laptop", "Electronics", 12, 74000),
    ("Phone",  "Electronics", 45, 23000),
    ("Tablet", "Electronics",  8, 35000),
    ("Mouse",  "Accessories", 120, 1500),
])
conn.commit(); conn.close()

st.title("SQL Query Agent")

#def tables():
#    st.title("Tables")

# ------

# ── 2. Connect LangChain SQL agent ───────────────────
db      = SQLDatabase.from_uri("sqlite:///sales.db")
llm     = ChatOpenAI(model="gpt-4o-mini", temperature=0)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type="openai-tools"
)

# ── 3. Business questions in plain English ────────────
questions = [
    "Who is our top customer by total spend? Show their name and total.",
    "Which products have stock below 15 units? I need to reorder soon.",
    "What is the total revenue from delivered orders only?",
    "List all customers who have ordered more than once.",
]