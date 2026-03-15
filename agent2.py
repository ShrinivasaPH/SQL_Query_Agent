import sqlite3
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="AI SQL Analyst",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI SQL Data Analyst")
st.caption("Ask questions in plain English and get SQL queries, data results, and insights instantly.")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -----------------------------
# Create sample database
# -----------------------------
conn = sqlite3.connect("sales.db")

conn.executescript("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer TEXT NOT NULL,
    product TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    status TEXT DEFAULT 'delivered'
);

CREATE TABLE IF NOT EXISTS products (
    name TEXT PRIMARY KEY,
    category TEXT,
    stock INTEGER,
    price REAL
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
    ("Tablet", "Electronics", 8, 35000),
    ("Mouse",  "Accessories", 120, 1500),
])

conn.commit()
conn.close()

# -----------------------------
# Preview database
# -----------------------------
st.divider()
st.subheader("Database Preview")

sales = pd.DataFrame({
    "id": [1, 2, 3, 4, 5, 6],
    "customer": ["Rahul Sharma", "Priya Mehta", "Arjun Nair", "Rahul Sharma", "Divya Krishnan", "Vikram Rao"],
    "product": ["Laptop", "Phone", "Tablet", "Mouse", "Laptop", "Phone"],
    "amount": [75000, 25000, 35000, 1500, 72000, 22000],
    "date": ["2024-01-05", "2024-01-12", "2024-01-18", "2024-01-20", "2024-01-22", "2024-01-28"],
    "status": ["delivered", "delivered", "returned", "delivered", "delivered", "delivered"]
})

st.dataframe(sales, use_container_width=True)

# -----------------------------
# LangChain SQL Agent
# -----------------------------
db = SQLDatabase.from_uri("sqlite:///sales.db")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type="openai-tools",
    agent_executor_kwargs={"return_intermediate_steps": True}
)

# -----------------------------
# Chat memory
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# Display conversation
# -----------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# Chat input
# -----------------------------
question = st.chat_input("Ask a question about the sales database...")

if question:

    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    # Assistant response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            result = agent.invoke({"input": question})

            answer = result["output"]
            sql_query = None

            # Extract SQL query
            for step in result["intermediate_steps"]:
                action = step[0]

                if hasattr(action, "tool_input") and isinstance(action.tool_input, dict):
                    if "query" in action.tool_input:
                        sql_query = action.tool_input["query"]
                        break

            # Show SQL query
            if sql_query:
                st.markdown("### Generated SQL")
                st.code(sql_query, language="sql")

            # Execute query
            conn = sqlite3.connect("sales.db")
            df = pd.read_sql_query(sql_query, conn)
            conn.close()

            # Show results
            st.markdown("### Query Result")
            st.dataframe(df, use_container_width=True)

            # Download button
            st.download_button(
                "Download CSV",
                df.to_csv(index=False),
                file_name="query_results.csv"
            )

            # Show insight
            st.markdown("### Insight")
            st.success(answer)

    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })