import streamlit as st
import pandas as pd
import altair as alt

# Load data
df = pd.read_json("products_all.json")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Overview", "Products", "Charts"])

# -----------------------------
# Charts Page
# -----------------------------
if page == "Charts":
    st.header("📊 Price Charts")

    # -----------------------------
    # 1) Price Distribution
    # -----------------------------
    st.subheader("Price Distribution (Histogram)")

    hist = (
        alt.Chart(df)
        .mark_bar(color="#A3C4F3")  # Pastel Blue
        .encode(
            alt.X("price:Q", bin=alt.Bin(maxbins=40), title="Price"),
            alt.Y("count()", title="Number of Products")
        )
        .properties(height=300)
    )

    st.altair_chart(hist, use_container_width=True)

    # -----------------------------
    # 2) Average Price per Store
    # -----------------------------
    st.subheader("Average Price per Store")

    avg_df = df.groupby("store")["price"].mean().reset_index()

    bar = (
        alt.Chart(avg_df)
        .mark_bar(color="#F7A4A4")  # Pastel Red
        .encode(
            x=alt.X("store:N", title="Store"),
            y=alt.Y("price:Q", title="Average Price"),
            tooltip=["store", "price"]
        )
        .properties(height=300)
    )

    st.altair_chart(bar, use_container_width=True)

    # -----------------------------
    # 3) Top 20 Cheapest Products
    # -----------------------------
    st.subheader("Top 20 Cheapest Products")

    top20 = df.sort_values("price").head(20)

    hbar = (
        alt.Chart(top20)
        .mark_bar(color="#C1E1C1")  # Pastel Green
        .encode(
            x=alt.X("price:Q", title="Price"),
            y=alt.Y("name:N", sort="-x", title="Product"),
            tooltip=["name", "price", "store"]
        )
        .properties(height=500)
    )

    st.altair_chart(hbar, use_container_width=True)
