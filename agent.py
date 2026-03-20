import sqlite3
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
import streamlit as st
import pandas as pd 
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="AI SQL Analyst",
    page_icon="📊",
    #layout="wide"
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

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

st.title(" :blue[📊 SQL Query Agent] :sunglasses: ✨")
st.markdown("Developed by: [Shrinivasa PH](https://www.linkedin.com/in/shrinivasa-ph-bb96a31b5/)")


st.info("SALES Table", icon="ℹ️")

sales = pd.DataFrame({
    "id": [1, 2, 3, 4, 5, 6],
    "customer": ["Rahul Sharma", "Priya Mehta", "Arjun Nair", "Rahul Sharma", "Divya Krishnan", "Vikram Rao"],
    "product": ["Laptop", "Phone", "Tablet", "Mouse", "Laptop", "Phone"],
    "amount": [75000, 25000, 35000, 1500, 72000, 22000],
    "date": ["2024-01-05", "2024-01-12", "2024-01-18", "2024-01-20", "2024-01-22", "2024-01-28"],
    "status": ["delivered", "delivered", "delivered", "delivered", "delivered", "delivered"]
})

st.table(sales)

def tables():
    st.title("Tables")

#pg = st.navigation([
#    st.Page("tables.py"),
#    #st.Page(tables)
#])

#pg.run()

# ------

# ── 2. Connect LangChain SQL agent ───────────────────
db      = SQLDatabase.from_uri("sqlite:///sales.db")
llm     = ChatOpenAI(model="gpt-4o-mini", temperature=0)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type="openai-tools",
    agent_executor_kwargs={"return_intermediate_steps": True}
)

#st.header("From English to SQL. Instantly. 😎")

#toolkit[]
st.subheader(" :blue[Ask anything about the Table. In Plain English!] :sunglasses: ✨")
question = st.text_area(
    " ",
    placeholder="Example: What is the total revenue from laptops?")
if st.button("Run Query 🚀"):
    st.subheader("User Question:")
    st.code(question)

    with st.spinner("Thinking..."):
        #st.caption("Question:", question)
        result = agent.invoke({"input": question})
        answer = result["output"]
        sql_query = None

        # Extract SQL query from intermediate steps
        for step in result["intermediate_steps"]:
            action = step[0]

            if hasattr(action, "tool_input") and isinstance(action.tool_input, dict):
                if "query" in action.tool_input:
                    sql_query = action.tool_input["query"]
                    break

    

        if sql_query:
            with st.container():
                st.divider()
                st.subheader("Generated SQL Query")
                st.code(sql_query, language="sql")

        conn = sqlite3.connect("sales.db")
        df = pd.read_sql_query(sql_query, conn)
        conn.close()

        st.divider()
        st.subheader("Query Result:")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            file_name="query_results.csv"
            
        )
        

        st.subheader("Insights! 📈")
        st.success(answer)
else:
    st.markdown(
    "<span style='background-color:#7c9460;color:white;padding:4px 10px;border-radius:10px;'>Enter a question & Hit Submit.</span>",
    unsafe_allow_html=True)
