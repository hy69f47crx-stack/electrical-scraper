import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# ---------------------------
# SESSION STATE (THEME TOGGLE)
# ---------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# ---------------------------
# THEME COLORS
# ---------------------------
LIGHT_BG = "#f7f3ef"
LIGHT_CARD = "rgba(255,255,255,0.55)"
LIGHT_BORDER = "#e8dcd3"
LIGHT_TEXT = "#2b2b2b"

DARK_BG = "#1a1a1a"
DARK_CARD = "rgba(30,30,30,0.55)"
DARK_BORDER = "#d9a6a0"  # Rose Gold
DARK_TEXT = "#f2f2f2"

# ---------------------------
# APPLY THEME
# ---------------------------
def apply_theme():
    if st.session_state.theme == "light":
        bg = LIGHT_BG
        card = LIGHT_CARD
        border = LIGHT_BORDER
        text = LIGHT_TEXT
    else:
        bg = DARK_BG
        card = DARK_CARD
        border = DARK_BORDER
        text = DARK_TEXT

    st.markdown(f"""
        <style>
        body {{
            background-color: {bg};
            color: {text};
        }}
        .glass-card {{
            background: {card};
            backdrop-filter: blur(4px);
            padding: 20px;
            border-radius: 14px;
            border: 1px solid {border};
            margin-bottom: 20px;
        }}
        .rose-border {{
            border-left: 4px solid {border};
            padding-left: 10px;
        }}
        </style>
    """, unsafe_allow_html=True)

apply_theme()

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:10px;'>⚙️ الإعدادات</h2>", unsafe_allow_html=True)
    if st.button("تبديل الثيم (Light / Dark)"):
        toggle_theme()
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("""
        <div class='glass-card'>
            <h4 style='margin-top:0;'>📁 الصفحات</h4>
        </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "",
        ["المنتجات", "مقارنة منتجين", "بحث ذكي", "التحليلات"],
        index=0
    )

# ---------------------------
# HEADER (STICKY)
# ---------------------------
st.markdown("""
    <style>
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 999;
        padding: 18px 10px;
        background: rgba(0,0,0,0);
        backdrop-filter: blur(4px);
        border-bottom: 1px solid rgba(200,200,200,0.15);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def header(title, desc):
    st.markdown(f"""
        <div class='sticky-header'>
            <h2 style='margin-bottom:4px;'>{title}</h2>
            <p style='margin-top:0; opacity:0.8;'>{desc}</p>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------
# SAMPLE DATA (PLACEHOLDER)
# ---------------------------
data = pd.DataFrame({
    "اسم المنتج": ["منتج A", "منتج B", "منتج C", "منتج D"],
    "السعر": [10.5, 12.0, 9.75, 15.2],
    "المتجر": ["متجر 1", "متجر 2", "متجر 1", "متجر 3"],
    "التصنيف": ["الكترونيات", "منزل", "الكترونيات", "مطبخ"]
})
# ---------------------------
# PAGE: المنتجات
# ---------------------------
def page_products():
    header("📦 المنتجات", "عرض المنتجات مع خيارات البحث والفرز والفلترة")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        search = st.text_input("🔍 بحث عن منتج")

    with col2:
        category = st.selectbox("📂 التصنيف", ["الكل"] + sorted(data["التصنيف"].unique()))

    with col3:
        sort_by = st.selectbox("↕️ ترتيب حسب", ["اسم المنتج", "السعر", "المتجر"])

    df = data.copy()

    if search:
        df = df[df["اسم المنتج"].str.contains(search, case=False)]

    if category != "الكل":
        df = df[df["التصنيف"] == category]

    df = df.sort_values(sort_by)

    st.dataframe(df, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Download
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button(
        "⬇️ تحميل Excel",
        data=buffer.getvalue(),
        file_name="products.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---------------------------
# PAGE: مقارنة منتجين
# ---------------------------
def page_compare():
    header("⚖️ مقارنة منتجين", "قارن بين منتجين من حيث السعر والمتجر والتصنيف")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        p1 = st.selectbox("اختر المنتج الأول", data["اسم المنتج"].unique())

    with col2:
        p2 = st.selectbox("اختر المنتج الثاني", data["اسم المنتج"].unique())

    if p1 and p2:
        d1 = data[data["اسم المنتج"] == p1].iloc[0]
        d2 = data[data["اسم المنتج"] == p2].iloc[0]

        comp = pd.DataFrame({
            "الميزة": ["السعر", "المتجر", "التصنيف"],
            p1: [d1["السعر"], d1["المتجر"], d1["التصنيف"]],
            p2: [d2["السعر"], d2["المتجر"], d2["التصنيف"]],
        })

        st.table(comp)

    st.markdown("</div>", unsafe_allow_html=True)
# ---------------------------
# PAGE: البحث الذكي
# ---------------------------
def page_smart_search():
    header("🧠 بحث ذكي", "ابحث باستخدام كلمات مفتاحية وسيقوم النظام بتحليل النتائج")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    query = st.text_input("اكتب كلمة مفتاحية للبحث")

    if query:
        df = data.copy()
        df = df[df["اسم المنتج"].str.contains(query, case=False) |
                df["التصنيف"].str.contains(query, case=False) |
                df["المتجر"].str.contains(query, case=False)]

        if len(df) == 0:
            st.warning("لا توجد نتائج مطابقة")
        else:
            st.success(f"تم العثور على {len(df)} نتيجة")
            st.dataframe(df, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# PAGE: التحليلات
# ---------------------------
def page_analytics():
    header("📊 التحليلات", "رسوم بيانية وتحليل الأسعار")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    fig = px.bar(
        data,
        x="اسم المنتج",
        y="السعر",
        color="التصنيف",
        title="مقارنة الأسعار حسب المنتج"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    fig2 = px.pie(
        data,
        names="التصنيف",
        title="توزيع المنتجات حسب التصنيف"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
# ---------------------------
# PAGE ROUTER
# ---------------------------
def router():
    if page == "المنتجات":
        page_products()
    elif page == "مقارنة منتجين":
        page_compare()
    elif page == "بحث ذكي":
        page_smart_search()
    elif page == "التحليلات":
        page_analytics()

# ---------------------------
# MAIN EXECUTION
# ---------------------------
def main():
    router()

if __name__ == "__main__":
    main()
# ---------------------------
# EXTRA STYLE (IMPROVED UI)
# ---------------------------
st.markdown("""
<style>
/* Remove Streamlit default padding */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* Improve radio buttons */
.stRadio > div {
    gap: 8px;
}

/* Improve table font */
.dataframe tbody tr td {
    font-size: 15px;
}

/* Improve sidebar width */
[data-testid="stSidebar"] {
    width: 280px !important;
}

/* Smooth transitions */
* {
    transition: 0.25s ease-in-out;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("""
    <br><br>
    <div style='text-align:center; opacity:0.6; font-size:14px;'>
        تم الإنشاء بواسطة نظام تحليلي متقدم — Dashboard v1.0
    </div>
""", unsafe_allow_html=True)
# ---------------------------
# ADVANCED CARD COMPONENT
# ---------------------------
def glass_card(title, content_html):
    st.markdown(f"""
        <div class='glass-card rose-border'>
            <h4 style='margin-top:0; margin-bottom:10px;'>{title}</h4>
            <div>{content_html}</div>
        </div>
    """, unsafe_allow_html=True)

# Example usage inside pages (optional future expansion)
def example_card_usage():
    glass_card(
        "مثال على بطاقة زجاجية",
        """
        <p>هذه بطاقة زجاجية بتأثير Soft Glass وRose Gold Border.</p>
        <ul>
            <li>شفافية 55%</li>
            <li>Blur بقيمة 4px</li>
            <li>حدود Rose Gold</li>
        </ul>
        """
    )

# ---------------------------
# FUTURE: API INTEGRATION PLACEHOLDER
# ---------------------------
def fetch_api_data():
    # Placeholder for future API integration
    # Example:
    # response = requests.get("https://api.example.com/products")
    # return response.json()
    return {
        "status": "ready",
        "message": "API integration placeholder active"
    }

# ---------------------------
# FUTURE: SCRAPER PLACEHOLDER
# ---------------------------
def run_scraper():
    # Placeholder for scraper integration
    return {
        "scraper": "ready",
        "items_found": 0
    }
# ---------------------------
# ADVANCED LAYOUT COMPONENTS
# ---------------------------
def two_column_card(title_left, content_left, title_right, content_right):
    col1, col2 = st.columns(2)

    with col1:
        glass_card(title_left, content_left)

    with col2:
        glass_card(title_right, content_right)

def three_column_card(t1, c1, t2, c2, t3, c3):
    col1, col2, col3 = st.columns(3)

    with col1:
        glass_card(t1, c1)

    with col2:
        glass_card(t2, c2)

    with col3:
        glass_card(t3, c3)

# ---------------------------
# FUTURE: METRICS PLACEHOLDER
# ---------------------------
def metrics_placeholder():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("عدد المنتجات", len(data))

    with col2:
        st.metric("أعلى سعر", f"{data['السعر'].max()} د.ك")

    with col3:
        st.metric("أقل سعر", f"{data['السعر'].min()} د.ك")

# ---------------------------
# OPTIONAL: DASHBOARD HOME (DISABLED)
# ---------------------------
def home_page():
    header("🏠 الرئيسية", "نظرة عامة على النظام")

    metrics_placeholder()

    three_column_card(
        "📦 المنتجات",
        "<p>عرض جميع المنتجات مع خيارات البحث والفرز.</p>",
        "⚖️ المقارنة",
        "<p>مقارنة منتجين من حيث السعر والمتجر.</p>",
        "📊 التحليلات",
        "<p>رسوم بيانية وتحليل الأسعار.</p>"
    )
# ---------------------------
# ADVANCED SEARCH ENGINE (FUTURE)
# ---------------------------
def advanced_search_engine(keyword):
    keyword = keyword.strip().lower()

    df = data.copy()

    df = df[
        df["اسم المنتج"].str.lower().str.contains(keyword) |
        df["التصنيف"].str.lower().str.contains(keyword) |
        df["المتجر"].str.lower().str.contains(keyword)
    ]

    score = []
    for _, row in df.iterrows():
        s = 0
        if keyword in row["اسم المنتج"].lower():
            s += 3
        if keyword in row["التصنيف"].lower():
            s += 2
        if keyword in row["المتجر"].lower():
            s += 1
        score.append(s)

    df["درجة التطابق"] = score
    df = df.sort_values("درجة التطابق", ascending=False)

    return df

# ---------------------------
# SMART SEARCH (UPGRADED)
# ---------------------------
def page_smart_search_v2():
    header("🔎 بحث ذكي متقدم", "محرك بحث يعتمد على خوارزمية تطابق الكلمات")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    query = st.text_input("اكتب كلمة للبحث")

    if query:
        results = advanced_search_engine(query)

        if len(results) == 0:
            st.warning("لا توجد نتائج مطابقة")
        else:
            st.success(f"تم العثور على {len(results)} نتيجة")
            st.dataframe(results, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
# ---------------------------
# EXPORT UTILITIES
# ---------------------------
def export_dataframe(df, filename="export.xlsx"):
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    return buffer.getvalue(), filename

def export_csv(df, filename="export.csv"):
    return df.to_csv(index=False).encode("utf-8"), filename

# ---------------------------
# EXPORT SECTION (OPTIONAL)
# ---------------------------
def export_section(df):
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📤 تصدير البيانات")

    col1, col2 = st.columns(2)

    with col1:
        excel_data, excel_name = export_dataframe(df)
        st.download_button(
            "⬇️ تحميل Excel",
            data=excel_data,
            file_name=excel_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col2:
        csv_data, csv_name = export_csv(df)
        st.download_button(
            "⬇️ تحميل CSV",
            data=csv_data,
            file_name=csv_name,
            mime="text/csv"
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# ENHANCED ANALYTICS (FUTURE)
# ---------------------------
def analytics_price_distribution():
    fig = px.histogram(
        data,
        x="السعر",
        nbins=10,
        title="توزيع الأسعار"
    )
    st.plotly_chart(fig, use_container_width=True)
# ---------------------------
# ADVANCED ANALYTICS: CATEGORY COUNT
# ---------------------------
def analytics_category_count():
    cat_count = data["التصنيف"].value_counts().reset_index()
    cat_count.columns = ["التصنيف", "عدد المنتجات"]

    fig = px.bar(
        cat_count,
        x="التصنيف",
        y="عدد المنتجات",
        title="عدد المنتجات حسب التصنيف",
        color="التصنيف"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# ADVANCED ANALYTICS: STORE PRICE AVERAGE
# ---------------------------
def analytics_store_avg():
    store_avg = data.groupby("المتجر")["السعر"].mean().reset_index()
    store_avg.columns = ["المتجر", "متوسط السعر"]

    fig = px.line(
        store_avg,
        x="المتجر",
        y="متوسط السعر",
        markers=True,
        title="متوسط السعر حسب المتجر"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# ANALYTICS MASTER PAGE (UPGRADED)
# ---------------------------
def page_analytics_v2():
    header("📊 تحليلات متقدمة", "مجموعة من الرسوم البيانية المتقدمة")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 توزيع الأسعار")
    analytics_price_distribution()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 عدد المنتجات حسب التصنيف")
    analytics_category_count()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 متوسط السعر حسب المتجر")
    analytics_store_avg()
    st.markdown("</div>", unsafe_allow_html=True)
# ---------------------------
# ADVANCED COMPARISON ENGINE (FUTURE)
# ---------------------------
def compare_products_advanced(p1, p2):
    d1 = data[data["اسم المنتج"] == p1].iloc[0]
    d2 = data[data["اسم المنتج"] == p2].iloc[0]

    score_price = 1 if d1["السعر"] < d2["السعر"] else 0
    score_store = 1 if d1["المتجر"] != d2["المتجر"] else 0
    score_category = 1 if d1["التصنيف"] == d2["التصنيف"] else 0

    result = pd.DataFrame({
        "الميزة": ["السعر الأقل", "اختلاف المتجر", "نفس التصنيف"],
        p1: [score_price, score_store, score_category],
        p2: [1 - score_price, 1 - score_store, 1 - score_category]
    })

    return result

# ---------------------------
# PAGE: مقارنة متقدمة
# ---------------------------
def page_compare_v2():
    header("⚖️ مقارنة متقدمة", "مقارنة ذكية بين منتجين مع تحليل نقاط القوة")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        p1 = st.selectbox("اختر المنتج الأول", data["اسم المنتج"].unique(), key="cmp1")

    with col2:
        p2 = st.selectbox("اختر المنتج الثاني", data["اسم المنتج"].unique(), key="cmp2")

    if p1 and p2:
        st.subheader("📌 جدول المقارنة الذكي")
        comp = compare_products_advanced(p1, p2)
        st.table(comp)

        st.subheader("📌 مقارنة الأسعار")
        fig = px.bar(
            data[data["اسم المنتج"].isin([p1, p2])],
            x="اسم المنتج",
           
# ---------------------------
# ADVANCED FILTER ENGINE
# ---------------------------
def filter_engine(df, price_min=None, price_max=None, store=None, category=None):
    result = df.copy()

    if price_min is not None:
        result = result[result["السعر"] >= price_min]

    if price_max is not None:
        result = result[result["السعر"] <= price_max]

    if store and store != "الكل":
        result = result[result["المتجر"] == store]

    if category and category != "الكل":
        result = result[result["التصنيف"] == category]

    return result

# ---------------------------
# PAGE: فلترة متقدمة
# ---------------------------
def page_filter_v2():
    header("🧪 فلترة متقدمة", "تحكم كامل في نطاق الأسعار والمتاجر والتصنيفات")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        price_min = st.number_input("السعر الأدنى", min_value=0.0, value=0.0)

    with col2:
        price_max = st.number_input("السعر الأعلى", min_value=0.0, value=float(data["السعر"].max()))

    with col3:
        store = st.selectbox("المتجر", ["الكل"] + sorted(data["المتجر"].unique()))

    with col4:
        category = st.selectbox("التصنيف", ["الكل"] + sorted(data["التصنيف"].unique()))

    filtered = filter_engine(data, price_min, price_max, store, category)

    st.subheader("📌 النتائج")
    st.dataframe(filtered, use_container_width=True)

    export_section(filtered)

    st.markdown("</div>", unsafe_allow_html=True)
# ---------------------------
# PAGE: لوحة التحكم المتقدمة (DASHBOARD PRO)
# ---------------------------
def page_dashboard_pro():
    header("📈 لوحة التحكم المتقدمة", "نظرة شاملة على أداء المنتجات والمتاجر")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 مؤشرات سريعة")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("عدد المنتجات", len(data))

    with col2:
        st.metric("أعلى سعر", f"{data['السعر'].max()} د.ك")

    with col3:
        st.metric("أقل سعر", f"{data['السعر'].min()} د.ك")

    with col4:
        st.metric("عدد المتاجر", data['المتجر'].nunique())

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 متوسط الأسعار حسب التصنيف")

    avg_by_cat = data.groupby("التصنيف")["السعر"].mean().reset_index()
    fig = px.bar(
        avg_by_cat,
        x="التصنيف",
        y="السعر",
        title="متوسط السعر لكل تصنيف",
        color="التصنيف"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 متوسط الأسعار حسب المتجر")

    avg_by_store = data.groupby("المتجر")["السعر"].mean().reset_index()
    fig2 = px.line(
        avg_by_store,
        x="المتجر",
        y="السعر",
        markers=True,
        title="متوسط السعر لكل متجر"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
# ---------------------------
# PAGE: لوحة التحكم الشاملة (ULTRA DASHBOARD)
# ---------------------------
def page_dashboard_ultra():
    header("🚀 لوحة التحكم الشاملة", "أقوى لوحة تحكم — دمج كامل بين التحليلات والفلترة والمقارنات")

    # --- SECTION 1: METRICS ---
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 مؤشرات عامة")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("عدد المنتجات", len(data))

    with col2:
        st.metric("عدد التصنيفات", data["التصنيف"].nunique())

    with col3:
        st.metric("عدد المتاجر", data["المتجر"].nunique())

    with col4:
        st.metric("متوسط الأسعار", f"{round(data['السعر'].mean(), 2)} د.ك")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- SECTION 2: FILTER + TABLE ---
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 فلترة سريعة")

    col1, col2 = st.columns(2)

    with col1:
        cat = st.selectbox("التصنيف", ["الكل"] + sorted(data["التصنيف"].unique()), key="ultra_cat")

    with col2:
        store = st.selectbox("المتجر", ["الكل"] + sorted(data["المتجر"].unique()), key="ultra_store")

    df = data.copy()

    if cat != "الكل":
        df = df[df["التصنيف"] == cat]

    if store != "الكل":
        df = df[df["المتجر"] == store]

    st.dataframe(df, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # --- SECTION 3: CHARTS ---
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 تحليل الأسعار")

    fig = px.box(
        df,
        x="التصنيف",
        y="السعر",
        title="تحليل تشتت الأسعار حسب التصنيف"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
# ---------------------------
# FINAL ROUTER (MASTER MENU)
# ---------------------------
def master_router():
    menu = st.sidebar.selectbox(
        "📁 اختر صفحة متقدمة",
        [
            "—",
            "بحث ذكي متقدم",
            "مقارنة متقدمة",
            "فلترة متقدمة",
            "تحليلات متقدمة",
            "لوحة التحكم المتقدمة",
            "لوحة التحكم الشاملة"
        ]
    )

    if menu == "بحث ذكي متقدم":
        page_smart_search_v2()

    elif menu == "مقارنة متقدمة":
        page_compare_v2()

    elif menu == "فلترة متقدمة":
        page_filter_v2()

    elif menu == "تحليلات متقدمة":
        page_analytics_v2()

    elif menu == "لوحة التحكم المتقدمة":
        page_dashboard_pro()

    elif menu == "لوحة التحكم الشاملة":
        page_dashboard_ultra()

# ---------------------------
# ACTIVATE MASTER ROUTER
# ---------------------------
master_router()
