import streamlit as st
import pandas as pd

st.markdown(
    "<span style='background-color:#1f77b4;color:white;padding:4px 10px;border-radius:10px;'>sales</span>",
    unsafe_allow_html=True
)

sales = pd.DataFrame({
    "id": [1, 2, 3, 4, 5, 6],
    "customer": ["Rahul Sharma", "Priya Mehta", "Arjun Nair", "Rahul Sharma", "Divya Krishnan", "Vikram Rao"],
    "product": ["Laptop", "Phone", "Tablet", "Mouse", "Laptop", "Phone"],
    "amount": [75000, 25000, 35000, 1500, 72000, 22000],
    "date": ["2024-01-05", "2024-01-12", "2024-01-18", "2024-01-20", "2024-01-22", "2024-01-28"],
    "status": ["delivered", "delivered", "delivered", "delivered", "delivered", "delivered"]
})

st.table(sales)

