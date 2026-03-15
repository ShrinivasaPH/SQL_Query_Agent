import streamlit as st
import pandas as pd 

pages = {
    "tables": [
        st.Page("tables.py", title="Tables"),
        #st.Page("manage_account.py", title="Manage your account"),
    ],
    #"Resources": [
    #    st.Page("learn.py", title="Learn about us"),
    #    st.Page("trial.py", title="Try it out"),
    #],
}

pg = st.navigation(pages)
pg.run()