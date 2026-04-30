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

# قسم الـ Overview
st.subheader("📌 Overview — نظرة عامة")

col1, col2, col3 = st.columns(3)
col1.metric("عدد المنتجات", len(df))
col2.metric("عدد المتاجر", df["store"].nunique())
col3.metric("آخر تحديث", df["timestamp"].max())

# جدول المنتجات
st.subheader("📦 المنتجات — Products Table")
st.dataframe(df, use_container_width=True)
