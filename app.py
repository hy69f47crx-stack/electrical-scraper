
import streamlit as st
import requests
import pandas as pd
import sqlite3

API_URL = "http://127.0.0.1:8000/price"

st.title("🔍 Multi‑Store Price Checker")

product_name = st.text_input("اسم المنتج:")

if st.button("بحث"):
    response = requests.get(API_URL, params={"product": product_name})
    data = response.json()

    if "error" in data:
        st.error(data["error"])
    else:
        st.subheader(f"الأسعار لمنتج: {product_name}")
        st.write(data["prices"])
