import streamlit as st
import pandas as pd
import altair as alt

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="Electrical Market Dashboard",
    page_icon="💡",
    layout="wide",
)

# ---------------------------------------------------
# Inject Custom CSS (Pastel Theme)
# ---------------------------------------------------
st.markdown("""
<style>

body {
    background-color: #FAFAFA;
}

.sidebar .sidebar-content {
    background-color: #F7F7F7;
}

.metric-card {
    padding: 20px;
    border-radius: 12px;
    background-color: #FFFFFF;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    text-align: center;
}

h1, h2, h3 {
    color: #444444;
}

.dataframe {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Load Data
# ---------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_json("products_all.json")

    # Clean price column
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])

    return df

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
    st.title("💡 Electrical Market Dashboard")
    st.markdown("لوحة متابعة لأسعار ومنتجات المتاجر الكهربائية.")

    # KPIs
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Products</h3>
            <h2>{len(df)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Stores</h3>
            <h2>{df['store'].nunique()}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        last_update = df['date'].max() if "date" in df.columns else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <h3>Last Update</h3>
            <h2>{last_update}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("Quick Glance")

    col4, col5 = st.columns(2)
    with col4:
        st.write("🔹 أسعار متفاوتة بين المتاجر")
        st.write("🔹 إمكانية مقارنة الأسعار")
    with col5:
        st.write("🔹 بيانات تتحدث تلقائيًا")
        st.write("🔹 جاهزة للتوسع (Risk, Growth, Alerts)")

# ---------------------------------------------------
# Products Page
# ---------------------------------------------------
elif page == "Products":
    st.title("📦 Products List")

    st.subheader("Filters")

    col1, col2, col3 = st.columns(3)

    # Search by name
    with col1:
        search = st.text_input("Search by product name:")

    # Store filter
    with col2:
        stores = ["All"] + sorted(df["store"].unique().tolist())
        selected_store = st.selectbox("Store", stores)

    # Price range filter
    with col3:
        min_price = float(df["price"].min())
        max_price = float(df["price"].max())

        if min_price == max_price:
            price_range = (min_price, max_price)
            st.info(f"All products have the same price: {min_price}")
        else:
            price_range = st.slider(
                "Price range",
                min_value=min_price,
                max_value=max_price,
                value=(min_price, max_price),
            )

    # Apply filters
    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[filtered_df["name"].str.contains(search, case=False)]

    if selected_store != "All":
        filtered_df = filtered_df[filtered_df["store"] == selected_store]

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
        .mark_bar(color="#A3C4F3")
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
        .mark_bar(color="#F7A4A4")
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
        .mark_bar(color="#C1E1C1")
        .encode(
            x=alt.X("price:Q", title="Price"),
            y=alt.Y("name:N", sort="-x", title="Product"),
            tooltip=["name", "price", "store"]
        )
        .properties(height=500)
    )

    st.altair_chart(hbar, use_container_width=True)

    # ---------------------------------------------------
    # Advanced Store Comparison
    # ---------------------------------------------------
    st.subheader("🏪 Advanced Store Comparison")

    # 1) Median Price per Store
    median_df = df.groupby("store")["price"].median().reset_index()

    median_chart = (
        alt.Chart(median_df)
        .mark_bar(color="#FFD6A5")
        .encode(
            x=alt.X("store:N", title="Store"),
            y=alt.Y("price:Q", title="Median Price"),
            tooltip=["store", "price"]
        )
        .properties(height=300)
    )

    st.altair_chart(median_chart, use_container_width=True)

    # 2) Price Range per Store
    range_df = df.groupby("store")["price"].agg(["min", "max"]).reset_index()

    range_chart = (
        alt.Chart(range_df)
        .mark_rule(color="#BDB2FF")
        .encode(
            x="store:N",
            y="min:Q",
            y2="max:Q",
            tooltip=["store", "min", "max"]
        )
        .properties(height=300)
    )

    st.altair_chart(range_chart, use_container_width=True)

    # 3) Box Plot per Store
    st.subheader("Price Distribution per Store (Box Plot)")

    box_chart = (
        alt.Chart(df)
        .mark_boxplot(color="#A0C4FF")
        .encode(
            x="store:N",
            y="price:Q",
            tooltip=["store", "price"]
        )
        .properties(height=350)
    )

    st.altair_chart(box_chart, use_container_width=True)

    # 4) Store Price Stability Score
    st.subheader("Store Price Stability Score")

    score_df = df.groupby("store")["price"].var().reset_index()
    score_df["score"] = 1 / (1 + score_df["price"])

    score_chart = (
        alt.Chart(score_df)
        .mark_bar(color="#C1E1C1")
        .encode(
            x="store:N",
            y="score:Q",
            tooltip=["store", "score"]
        )
        .properties(height=300)
    )

    st.altair_chart(score_chart, use_container_width=True)
