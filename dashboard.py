import streamlit as st
import pandas as pd
import altair as alt

# ---------------------------------------------------
# Load Data
# ---------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_json("products_all.json")

df = load_data()

# ---------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Overview", "Products", "Charts"])

# ---------------------------------------------------
# Overview Page
# ---------------------------------------------------
if page == "Overview":
    st.title("📊 Electrical Market Dashboard")

    # KPIs
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Products", len(df))
    col2.metric("Stores", df['store'].nunique())
    col3.metric("Last Update", df['date'].max() if "date" in df.columns else "N/A")

    st.write("---")
    st.subheader("Products Summary")
    st.write("This dashboard shows scraped product data from multiple electrical stores.")

# ---------------------------------------------------
# Products Page
# ---------------------------------------------------
elif page == "Products":
    st.title("📦 Products List")

    # --- Filters Section ---
    st.subheader("Filters")

    col1, col2, col3 = st.columns(3)

    # Search by name
    with col1:
        search = st.text_input("Search by product name:")

    # Filter by store
    with col2:
        stores = ["All"] + sorted(df["store"].unique().tolist())
        selected_store = st.selectbox("Store", stores)

    # Filter by price range
    with col3:
        min_price = float(df["price"].min())
        max_price = float(df["price"].max())
        price_range = st.slider(
            "Price range",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
        )

    # --- Apply Filters ---
    filtered_df = df.copy()

    # Name filter
    if search:
        filtered_df = filtered_df[filtered_df["name"].str.contains(search, case=False)]

    # Store filter
    if selected_store != "All":
        filtered_df = filtered_df[filtered_df["store"] == selected_store]

    # Price filter
    filtered_df = filtered_df[
        (filtered_df["price"] >= price_range[0]) &
        (filtered_df["price"] <= price_range[1])
    ]

    st.write(f"Showing {len(filtered_df)} products")
    st.dataframe(filtered_df, use_container_width=True)


# ---------------------------------------------------
# Charts Page
# ---------------------------------------------------
elif page == "Charts":
    st.header("📈 Price Charts")

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
