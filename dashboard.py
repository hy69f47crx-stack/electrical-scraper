import streamlit as st
import pandas as pd
import json
import altair as alt

# -----------------------------
# إعداد الصفحة العامة
# -----------------------------
st.set_page_config(
    page_title="مقارنة أسعار الأجهزة الكهربائية",
    page_icon="💡",
    layout="wide"
)

# -----------------------------
# CSS — ثيم مودرن + Glassmorphism
# -----------------------------
st.markdown("""
<style>

html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
    font-family: "Cairo", sans-serif;
    background-color: #F4F6FB;
}

/* Glass Cards */
.glass-card {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 1.4rem;
    border: 1px solid rgba(255,255,255,0.3);
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}

/* KPI Cards */
.kpi {
    background: rgba(255,255,255,0.85);
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.4);
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    transition: 0.2s;
}
.kpi h3 {
    margin: 0;
    font-size: 1.6rem;
}
.kpi p {
    margin: 0;
    color: #64748B;
    font-size: 0.9rem;
}
.kpi:hover {
    transform: translateY(-4px);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #6C63FF, #A78BFA);
    color: white;
    border-radius: 12px;
    padding: 0.6rem 1.4rem;
    border: none;
    font-weight: 600;
    transition: 0.2s;
}
.stButton>button:hover {
    transform: scale(1.03);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(10px);
    border-left: 1px solid rgba(255,255,255,0.4);
}

/* Tables */
.dataframe tbody tr:hover {
    background-color: #EEF2FF !important;
}

/* Header */
.header {
    padding: 1.5rem;
    border-radius: 16px;
    background: linear-gradient(135deg, #6C63FF, #A78BFA);
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
.header h2 {
    margin-bottom: 0.3rem;
}
.header p {
    margin: 0;
    opacity: 0.9;
}

/* Small text */
.muted {
    color: #64748B;
    font-size: 0.85rem;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# تحميل البيانات
# -----------------------------
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

products = load_json("products_all.json")
groups = load_json("matched_groups.json")

df_products = pd.DataFrame(products)
df_groups = pd.DataFrame(groups)

# -----------------------------
# صفحة تسجيل الدخول
# -----------------------------
def login_page():
    st.markdown("""
    <div class="glass-card">
        <h3>🔐 تسجيل الدخول</h3>
        <p class="muted">هذه الواجهة مخصصة للوصول إلى لوحة التحكم.</p>
    </div>
    """, unsafe_allow_html=True)

    password = st.text_input("أدخل كلمة المرور", type="password")

    if password == "fahad2026":
        st.session_state["logged_in"] = True
        st.rerun()
    elif password:
        st.error("كلمة المرور غير صحيحة")

if "logged_in" not in st.session_state:
    login_page()
    st.stop()

# -----------------------------
# القائمة الجانبية
# -----------------------------
st.sidebar.markdown("### ⚙️ التحكم")
page = st.sidebar.radio(
    "القائمة الرئيسية",
    [
        "الرئيسية",
        "المنتجات",
        "مقارنة الأسعار",
        "أفضل العروض",
        "تفاصيل المنتج",
        "الرسوم البيانية"
    ]
)

# -----------------------------
# صفحة الرئيسية
# -----------------------------
def show_home():
    st.markdown("""
    <div class="header">
        <h2>💡 منصة مقارنة أسعار الأجهزة الكهربائية</h2>
        <p>تجميع ذكي لأسعار المتاجر الكويتية + مطابقة تلقائية + واجهة احترافية.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f'<div class="kpi"><h3>{len(df_products)}</h3><p>عدد المنتجات</p></div>',
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f'<div class="kpi"><h3>{len(df_groups)}</h3><p>مجموعات المطابقة</p></div>',
            unsafe_allow_html=True
        )

    with c3:
        stores = df_products["store"].nunique() if not df_products.empty else 0
        st.markdown(
            f'<div class="kpi"><h3>{stores}</h3><p>عدد المتاجر</p></div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="glass-card"><h3>🔥 أفضل فرص التوفير</h3>', unsafe_allow_html=True)
    if not df_groups.empty:
        top = df_groups.sort_values("savings_pct", ascending=False).head(10)
        st.dataframe(top, use_container_width=True)
    else:
        st.info("لا توجد بيانات مطابقة بعد.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# صفحة المنتجات
# -----------------------------
def show_products():
    st.markdown('<div class="glass-card"><h3>🧾 جميع المنتجات</h3></div>', unsafe_allow_html=True)

    if df_products.empty:
        st.info("لا توجد بيانات بعد.")
        return

    # فلاتر بسيطة
    col1, col2 = st.columns(2)
    with col1:
        stores = ["الكل"] + sorted(df_products["store"].dropna().unique().tolist())
        store_filter = st.selectbox("المتجر", stores)
    with col2:
        query = st.text_input("بحث بالاسم أو الموديل")

    df = df_products.copy()

    if store_filter != "الكل":
        df = df[df["store"] == store_filter]

    if query:
        df = df[df["name"].str.contains(query, case=False, na=False)]

    st.dataframe(df, use_container_width=True)

# -----------------------------
# صفحة مقارنة الأسعار
# -----------------------------
def show_comparison():
    st.markdown('<div class="glass-card"><h3>🔍 مقارنة الأسعار بين المتاجر</h3></div>', unsafe_allow_html=True)

    if df_groups.empty:
        st.info("لا توجد بيانات مطابقة بعد.")
        return

    df = df_groups.copy()
    df["أفضل سعر"] = df["best_price"].apply(lambda x: f"🟢 {x} KD")
    df["أسوأ سعر"] = df["worst_price"].apply(lambda x: f"🔴 {x} KD")

    st.dataframe(
        df[["canonical_name", "best_store", "أفضل سعر", "أسوأ سعر", "savings_pct"]],
        use_container_width=True
    )

# -----------------------------
# صفحة أفضل العروض
# -----------------------------
def show_best_deals():
    st.markdown('<div class="glass-card"><h3>🏆 أفضل العروض</h3></div>', unsafe_allow_html=True)

    if df_groups.empty:
        st.info("لا توجد بيانات مطابقة بعد.")
        return

    top = df_groups.sort_values("savings_pct", ascending=False).head(20)
    st.dataframe(top, use_container_width=True)

# -----------------------------
# صفحة تفاصيل المنتج
# -----------------------------
def show_details():
    st.markdown('<div class="glass-card"><h3>📦 تفاصيل المنتج</h3></div>', unsafe_allow_html=True)

    if df_groups.empty:
        st.info("لا توجد بيانات مطابقة بعد.")
        return

    names = df_groups["canonical_name"].unique()
    choice = st.selectbox("اختر المنتج", names)

    group = df_groups[df_groups["canonical_name"] == choice].iloc[0]

    st.markdown(f"""
    <div class="glass-card">
        <h3>{choice}</h3>
        <p><b>أفضل سعر:</b> 🟢 {group['best_price']} KD — {group['best_store']}</p>
        <p><b>أسوأ سعر:</b> 🔴 {group['worst_price']} KD</p>
        <p><b>نسبة التوفير:</b> {group['savings_pct']}%</p>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# صفحة الرسوم البيانية
# -----------------------------
def show_charts():
    st.markdown('<div class="glass-card"><h3>📊 الرسوم البيانية</h3></div>', unsafe_allow_html=True)

    if df_products.empty:
        st.info("لا توجد بيانات بعد.")
        return

    chart = alt.Chart(df_products).mark_bar().encode(
        x="store:N",
        y="price:Q",
        tooltip=["store", "price"]
    ).properties(
        height=400
    )

    st.altair_chart(chart, use_container_width=True)

# -----------------------------
# تشغيل الصفحات
# -----------------------------
if page == "الرئيسية":
    show_home()
elif page == "المنتجات":
    show_products()
elif page == "مقارنة الأسعار":
    show_comparison()
elif page == "أفضل العروض":
    show_best_deals()
elif page == "تفاصيل المنتج":
    show_details()
elif page == "الرسوم البيانية":
    show_charts()
