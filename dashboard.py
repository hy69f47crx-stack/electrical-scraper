import json
import pandas as pd
import streamlit as st

# إعداد الصفحة
st.set_page_config(
    page_title="Price Dashboard — لوحة متابعة الأسعار",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Price Dashboard — لوحة متابعة الأسعار")

# تحميل البيانات
try:
    with open("products_all.json", "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
except Exception as e:
    st.error("⚠️ لا يمكن تحميل ملف المنتجات. تأكد من وجود products_all.json")
    st.stop()

# التأكد من وجود الأعمدة
required_columns = ["name", "price", "store", "timestamp"]

for col in required_columns:
    if col not in df.columns:
        df[col] = "N/A"

# قسم الـ Overview
st.subheader("📌 Overview — نظرة عامة")

col1, col2, col3 = st.columns(3)

col1.metric("عدد المنتجات", len(df))

if "store" in df.columns:
    col2.metric("عدد المتاجر", df["store"].nunique())
else:
    col2.metric("عدد المتاجر", "N/A")

if "timestamp" in df.columns:
    col3.metric("آخر تحديث", df["timestamp"].max())
else:
    col3.metric("آخر تحديث", "N/A")

# جدول المنتجات
st.subheader("📦 المنتجات — Products Table")
st.dataframe(df, use_container_width=True)
