import json
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from pathlib import Path

# ---------------------------
# USERS & ROLES
# ---------------------------
USERS = {
    "admin":   {"password": "admin123",  "role": "مدير",    "name": "المدير"},
    "fahad":   {"password": "fahad2024", "role": "مشرف",    "name": "فهد"},
    "viewer":  {"password": "view123",   "role": "عارض",    "name": "زائر"},
}

# ---------------------------
# AUTH: SESSION STATE
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------------------
# LOGIN PAGE
# ---------------------------
def show_login():
    st.markdown("""
        <style>
        .login-wrap {
            max-width: 400px;
            margin: 80px auto 0 auto;
            padding: 40px;
            border-radius: 18px;
            background: rgba(255,255,255,0.6);
            backdrop-filter: blur(8px);
            border: 1px solid #e8dcd3;
            text-align: center;
        }
        .login-title { font-size: 26px; font-weight: 700; margin-bottom: 6px; }
        .login-sub   { font-size: 14px; opacity: 0.6; margin-bottom: 24px; }
        </style>
        <div class='login-wrap'>
            <div class='login-title'>🔐 تسجيل الدخول</div>
            <div class='login-sub'>نظام تتبع أسعار المنتجات الكهربائية</div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
        submitted = st.form_submit_button("دخول ←", use_container_width=True)

        if submitted:
            user = USERS.get(username.strip())
            if user and user["password"] == password:
                st.session_state.authenticated = True
                st.session_state.username      = username.strip()
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

if not st.session_state.authenticated:
    show_login()
    st.stop()

# ==============================
# EVERYTHING BELOW = PROTECTED
# ==============================

# ---------------------------
# CURRENT USER INFO
# ---------------------------
current_user = USERS[st.session_state.username]
USER_NAME    = current_user["name"]
USER_ROLE    = current_user["role"]

# ---------------------------
# TOP BAR (NAME + LOGOUT)
# ---------------------------
st.markdown("""
    <style>
    .topbar {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 14px;
        padding: 8px 16px 0 0;
        margin-bottom: -10px;
    }
    .topbar-user {
        font-size: 14px;
        opacity: 0.85;
        background: rgba(217,166,160,0.18);
        border: 1px solid #d9a6a0;
        border-radius: 20px;
        padding: 4px 14px;
    }
    </style>
""", unsafe_allow_html=True)

top_col1, top_col2 = st.columns([8, 2])
with top_col2:
    st.markdown(
        f"<div class='topbar'>"
        f"<span class='topbar-user'>👤 {USER_NAME} — {USER_ROLE}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
    if st.button("تسجيل خروج ↩", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username      = ""
        st.rerun()

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
LIGHT_BG    = "#f7f3ef"
LIGHT_CARD  = "rgba(255,255,255,0.55)"
LIGHT_BORDER = "#e8dcd3"
LIGHT_TEXT  = "#2b2b2b"

DARK_BG     = "#1a1a1a"
DARK_CARD   = "rgba(30,30,30,0.55)"
DARK_BORDER = "#d9a6a0"   # Rose Gold
DARK_TEXT   = "#f2f2f2"


def apply_theme():
    if st.session_state.theme == "light":
        bg, card, border, text = LIGHT_BG, LIGHT_CARD, LIGHT_BORDER, LIGHT_TEXT
    else:
        bg, card, border, text = DARK_BG, DARK_CARD, DARK_BORDER, DARK_TEXT

    st.markdown(f"""
        <style>
        body {{ background-color: {bg}; color: {text}; }}
        .glass-card {{
            background: {card};
            backdrop-filter: blur(4px);
            padding: 20px;
            border-radius: 14px;
            border: 1px solid {border};
            margin-bottom: 20px;
        }}
        .rose-border {{ border-left: 4px solid {border}; padding-left: 10px; }}
        .block-container {{ padding-top: 1rem; padding-bottom: 1rem; }}
        .stRadio > div {{ gap: 8px; }}
        .dataframe tbody tr td {{ font-size: 15px; }}
        [data-testid="stSidebar"] {{ width: 290px !important; }}
        * {{ transition: 0.25s ease-in-out; }}
        </style>
    """, unsafe_allow_html=True)


apply_theme()


# ---------------------------
# CATEGORY INFERENCE FROM PRODUCT NAME
# ---------------------------
def infer_category(name: str) -> str:
    """يستنتج تصنيف المنتج من اسمه."""
    n = name if isinstance(name, str) else ""
    if any(k in n for k in ["كيبل", "سلك", "Wire", "Cable", "NYY", "NYM", "XLPE", "كابل"]):
        return "كيبلات وأسلاك"
    if any(k in n for k in ["قاطع", "Breaker", "MCB", "RCD", "RCCB", "فيوز", "Fuse", "حماية"]):
        return "قواطع وحماية"
    if any(k in n for k in ["لمبة", "LED", "إضاءة", "Lamp", "ليد", "نيون", "Spotlight", "بلف"]):
        return "إضاءة"
    if any(k in n for k in ["مقبس", "Socket", "Plug", "أرضي", "تمديد", "Extension", "بريز"]):
        return "مقابس وتمديدات"
    if any(k in n for k in ["لوحة", "Panel", "صندوق", "Box", "توزيع", "مفتاح", "Switch"]):
        return "لوحات ومفاتيح"
    if any(k in n for k in ["مكيف", "Inverter", "Motor", "مضخة", "Pump", "كمبريسور"]):
        return "أجهزة كهربائية"
    return "متنوع"


# ---------------------------
# DATA LOADING (REAL DATA)
# ---------------------------
@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    """يحمّل المنتجات من products_all.json ويرجع DataFrame جاهزاً."""
    path = Path(__file__).parent / "products_all.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        df = pd.DataFrame(raw)
        df.rename(columns={
            "name":  "اسم المنتج",
            "price": "السعر",
            "store": "المتجر",
        }, inplace=True)
        df["السعر"] = pd.to_numeric(df["السعر"], errors="coerce")
        df = df.dropna(subset=["السعر"]).reset_index(drop=True)
        df["التصنيف"] = df["اسم المنتج"].apply(infer_category)
        return df
    except Exception as e:
        st.warning(f"تعذّر تحميل products_all.json — يُستخدم بيانات تجريبية ({e})")
        return pd.DataFrame({
            "اسم المنتج": ["كيبل NYY 3×2.5", "قاطع MCB 16A", "لمبة LED 9W", "مقبس 2P"],
            "السعر":      [1.85, 3.20, 0.95, 2.50],
            "المتجر":     ["دخيل الجسار", "العربية للكهرباء", "دخيل الجسار", "Extra"],
            "التصنيف":    ["كيبلات وأسلاك", "قواطع وحماية", "إضاءة", "مقابس وتمديدات"],
            "url":        ["", "", "", ""],
        })


data = load_data()


# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:10px;'>⚙️ الإعدادات</h2>", unsafe_allow_html=True)

    if st.button("تبديل الثيم (Light / Dark)"):
        toggle_theme()
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-bottom:8px;'>📁 الصفحات</h4>", unsafe_allow_html=True)

    page = st.radio(
        "",
        [
            "🏠 الرئيسية",
            "📦 المنتجات",
            "⚖️ مقارنة منتجين",
            "⚖️ مقارنة متقدمة",
            "🧠 بحث ذكي",
            "🔎 بحث متقدم",
            "🧪 فلترة متقدمة",
            "📊 التحليلات",
            "📈 لوحة التحكم المتقدمة",
            "🚀 لوحة التحكم الشاملة",
        ],
        index=0
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption(f"📦 {len(data)} منتج | 🏪 {data['المتجر'].nunique()} متاجر")


# ---------------------------
# STICKY HEADER STYLE
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
# UTILITY: EXPORT SECTION
# ---------------------------
def export_section(df: pd.DataFrame):
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📤 تصدير البيانات")
    col1, col2 = st.columns(2)

    with col1:
        try:
            buf = BytesIO()
            df.to_excel(buf, index=False, engine="openpyxl")
            st.download_button(
                "⬇️ تحميل Excel",
                data=buf.getvalue(),
                file_name="export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception:
            st.info("مكتبة openpyxl غير مثبّتة — تحميل CSV متاح")

    with col2:
        st.download_button(
            "⬇️ تحميل CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="export.csv",
            mime="text/csv",
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# PAGE: 🏠 الرئيسية
# ---------------------------
def page_home():
    header("🏠 الرئيسية", "نظرة عامة على نظام تتبع أسعار المنتجات الكهربائية")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("عدد المنتجات", len(data))
    with col2:
        st.metric("أعلى سعر", f"{data['السعر'].max():.3f} د.ك")
    with col3:
        st.metric("أقل سعر", f"{data['السعر'].min():.3f} د.ك")
    with col4:
        st.metric("عدد المتاجر", data["المتجر"].nunique())

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 آخر المنتجات المُجلبة")
    st.dataframe(
        data[["اسم المنتج", "السعر", "المتجر", "التصنيف"]].head(10),
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 توزيع المنتجات حسب المتجر")
    store_count = data["المتجر"].value_counts().reset_index()
    store_count.columns = ["المتجر", "عدد المنتجات"]
    fig = px.pie(store_count, names="المتجر", values="عدد المنتجات",
                 title="حصة كل متجر")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# PAGE: 📦 المنتجات
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
        df = df[df["اسم المنتج"].str.contains(search, case=False, na=False)]
    if category != "الكل":
        df = df[df["التصنيف"] == category]
    df = df.sort_values(sort_by)

    st.dataframe(df[["اسم المنتج", "السعر", "المتجر", "التصنيف"]], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    export_section(df[["اسم المنتج", "السعر", "المتجر", "التصنيف"]])


# ---------------------------
# PAGE: ⚖️ مقارنة منتجين (بسيطة)
# ---------------------------
def page_compare():
    header("⚖️ مقارنة منتجين", "قارن بين منتجين من حيث السعر والمتجر والتصنيف")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        p1 = st.selectbox("اختر المنتج الأول", data["اسم المنتج"].unique(), key="cmp1_basic")
    with col2:
        p2 = st.selectbox("اختر المنتج الثاني", data["اسم المنتج"].unique(), key="cmp2_basic")

    if p1 and p2:
        d1 = data[data["اسم المنتج"] == p1].iloc[0]
        d2 = data[data["اسم المنتج"] == p2].iloc[0]

        comp = pd.DataFrame({
            "الميزة": ["السعر", "المتجر", "التصنيف"],
            p1[:30]: [f"{d1['السعر']:.3f} د.ك", d1["المتجر"], d1["التصنيف"]],
            p2[:30]: [f"{d2['السعر']:.3f} د.ك", d2["المتجر"], d2["التصنيف"]],
        })
        st.table(comp)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# PAGE: ⚖️ مقارنة متقدمة
# ---------------------------
def compare_products_advanced(p1: str, p2: str) -> pd.DataFrame:
    d1 = data[data["اسم المنتج"] == p1].iloc[0]
    d2 = data[data["اسم المنتج"] == p2].iloc[0]

    return pd.DataFrame({
        "الميزة": ["السعر", "المتجر", "التصنيف", "الأرخص ✅"],
        p1[:30]: [
            f"{d1['السعر']:.3f} د.ك",
            d1["المتجر"],
            d1["التصنيف"],
            "✅" if d1["السعر"] <= d2["السعر"] else "",
        ],
        p2[:30]: [
            f"{d2['السعر']:.3f} د.ك",
            d2["المتجر"],
            d2["التصنيف"],
            "✅" if d2["السعر"] <= d1["السعر"] else "",
        ],
    })


def page_compare_v2():
    header("⚖️ مقارنة متقدمة", "مقارنة ذكية بين منتجين مع تحليل نقاط القوة")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        p1 = st.selectbox("اختر المنتج الأول", data["اسم المنتج"].unique(), key="cmp1_adv")
    with col2:
        p2 = st.selectbox("اختر المنتج الثاني", data["اسم المنتج"].unique(), key="cmp2_adv")

    if p1 and p2:
        st.subheader("📌 جدول المقارنة الذكي")
        comp = compare_products_advanced(p1, p2)
        st.table(comp)

        st.subheader("📌 مقارنة الأسعار")
        subset = data[data["اسم المنتج"].isin([p1, p2])].copy()
        fig = px.bar(
            subset,
            x="اسم المنتج",
            y="السعر",
            color="اسم المنتج",
            title="مقارنة السعر بين المنتجين",
            text_auto=".3f",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# PAGE: 🧠 بحث ذكي
# ---------------------------
def page_smart_search():
    header("🧠 بحث ذكي", "ابحث باستخدام كلمات مفتاحية")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    query = st.text_input("اكتب كلمة مفتاحية للبحث")
    if query:
        df = data[
            data["اسم المنتج"].str.contains(query, case=False, na=False) |
            data["التصنيف"].str.contains(query, case=False, na=False) |
            data["المتجر"].str.contains(query, case=False, na=False)
        ]
        if df.empty:
            st.warning("لا توجد نتائج مطابقة")
        else:
            st.success(f"تم العثور على {len(df)} نتيجة")
            st.dataframe(df[["اسم المنتج", "السعر", "المتجر", "التصنيف"]], use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# PAGE: 🔎 بحث متقدم (مع درجة التطابق)
# ---------------------------
def advanced_search_engine(keyword: str) -> pd.DataFrame:
    kw = keyword.strip().lower()
    df = data[
        data["اسم المنتج"].str.lower().str.contains(kw, na=False) |
        data["التصنيف"].str.lower().str.contains(kw, na=False) |
        data["المتجر"].str.lower().str.contains(kw, na=False)
    ].copy()

    scores = []
    for _, row in df.iterrows():
        s = 0
        if kw in str(row["اسم المنتج"]).lower():  s += 3
        if kw in str(row["التصنيف"]).lower():      s += 2
        if kw in str(row["المتجر"]).lower():       s += 1
        scores.append(s)
    df["درجة التطابق"] = scores
    return df.sort_values("درجة التطابق", ascending=False)


def page_smart_search_v2():
    header("🔎 بحث متقدم", "محرك بحث بخوارزمية تطابق الكلمات مع تقييم النتائج")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    query = st.text_input("اكتب كلمة للبحث", key="adv_search")
    if query:
        results = advanced_search_engine(query)
        if results.empty:
            st.warning("لا توجد نتائج مطابقة")
        else:
            st.success(f"تم العثور على {len(results)} نتيجة")
            st.dataframe(
                results[["اسم المنتج", "السعر", "المتجر", "التصنيف", "درجة التطابق"]],
                use_container_width=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# PAGE: 🧪 فلترة متقدمة
# ---------------------------
def page_filter_v2():
    header("🧪 فلترة متقدمة", "تحكم كامل في نطاق الأسعار والمتاجر والتصنيفات")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        price_min = st.number_input("السعر الأدنى", min_value=0.0, value=0.0, step=0.1)
    with col2:
        price_max = st.number_input("السعر الأعلى", min_value=0.0,
                                    value=float(data["السعر"].max()), step=0.1)
    with col3:
        store = st.selectbox("المتجر", ["الكل"] + sorted(data["المتجر"].unique()),
                             key="filter_store")
    with col4:
        category = st.selectbox("التصنيف", ["الكل"] + sorted(data["التصنيف"].unique()),
                                key="filter_cat")

    df = data.copy()
    df = df[(df["السعر"] >= price_min) & (df["السعر"] <= price_max)]
    if store != "الكل":
        df = df[df["المتجر"] == store]
    if category != "الكل":
        df = df[df["التصنيف"] == category]

    st.subheader(f"📌 النتائج ({len(df)} منتج)")
    st.dataframe(df[["اسم المنتج", "السعر", "المتجر", "التصنيف"]], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    export_section(df[["اسم المنتج", "السعر", "المتجر", "التصنيف"]])


# ---------------------------
# PAGE: 📊 التحليلات
# ---------------------------
def page_analytics():
    header("📊 التحليلات", "رسوم بيانية وتحليل الأسعار")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 توزيع الأسعار")
    fig = px.histogram(data, x="السعر", nbins=20, title="توزيع الأسعار",
                       color_discrete_sequence=["#d9a6a0"])
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 توزيع المنتجات حسب التصنيف")
    fig2 = px.pie(data, names="التصنيف", title="توزيع التصنيفات")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 متوسط السعر حسب المتجر")
    store_avg = data.groupby("المتجر")["السعر"].mean().reset_index()
    store_avg.columns = ["المتجر", "متوسط السعر"]
    fig3 = px.bar(store_avg, x="المتجر", y="متوسط السعر",
                  color="المتجر", title="متوسط السعر لكل متجر", text_auto=".3f")
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# PAGE: 📈 لوحة التحكم المتقدمة
# ---------------------------
def page_dashboard_pro():
    header("📈 لوحة التحكم المتقدمة", "نظرة شاملة على أداء المنتجات والمتاجر")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 مؤشرات سريعة")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("عدد المنتجات", len(data))
    with col2:
        st.metric("أعلى سعر", f"{data['السعر'].max():.3f} د.ك")
    with col3:
        st.metric("أقل سعر", f"{data['السعر'].min():.3f} د.ك")
    with col4:
        st.metric("عدد المتاجر", data["المتجر"].nunique())
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 متوسط الأسعار حسب التصنيف")
    avg_cat = data.groupby("التصنيف")["السعر"].mean().reset_index()
    fig = px.bar(avg_cat, x="التصنيف", y="السعر",
                 title="متوسط السعر لكل تصنيف", color="التصنيف", text_auto=".3f")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 متوسط الأسعار حسب المتجر")
    avg_store = data.groupby("المتجر")["السعر"].mean().reset_index()
    fig2 = px.line(avg_store, x="المتجر", y="السعر",
                   markers=True, title="متوسط السعر لكل متجر")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# PAGE: 🚀 لوحة التحكم الشاملة
# ---------------------------
def page_dashboard_ultra():
    header("🚀 لوحة التحكم الشاملة",
           "دمج التحليلات والفلترة والمقارنات في صفحة واحدة")

    # SECTION 1: METRICS
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
        st.metric("متوسط الأسعار", f"{data['السعر'].mean():.3f} د.ك")
    st.markdown("</div>", unsafe_allow_html=True)

    # SECTION 2: FILTER + TABLE
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 فلترة سريعة")
    col1, col2 = st.columns(2)
    with col1:
        cat = st.selectbox("التصنيف", ["الكل"] + sorted(data["التصنيف"].unique()),
                           key="ultra_cat")
    with col2:
        store = st.selectbox("المتجر", ["الكل"] + sorted(data["المتجر"].unique()),
                             key="ultra_store")

    df = data.copy()
    if cat != "الكل":
        df = df[df["التصنيف"] == cat]
    if store != "الكل":
        df = df[df["المتجر"] == store]

    st.dataframe(df[["اسم المنتج", "السعر", "المتجر", "التصنيف"]], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # SECTION 3: BOX CHART
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 تحليل تشتت الأسعار")
    if len(df) > 0:
        fig = px.box(df, x="التصنيف", y="السعر",
                     title="تشتت الأسعار حسب التصنيف", color="التصنيف")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات بعد تطبيق الفلتر")
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# MAIN ROUTER
# ---------------------------
def main():
    if   page == "🏠 الرئيسية":
        page_home()
    elif page == "📦 المنتجات":
        page_products()
    elif page == "⚖️ مقارنة منتجين":
        page_compare()
    elif page == "⚖️ مقارنة متقدمة":
        page_compare_v2()
    elif page == "🧠 بحث ذكي":
        page_smart_search()
    elif page == "🔎 بحث متقدم":
        page_smart_search_v2()
    elif page == "🧪 فلترة متقدمة":
        page_filter_v2()
    elif page == "📊 التحليلات":
        page_analytics()
    elif page == "📈 لوحة التحكم المتقدمة":
        page_dashboard_pro()
    elif page == "🚀 لوحة التحكم الشاملة":
        page_dashboard_ultra()


main()

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("""
    <br><br>
    <div style='text-align:center; opacity:0.6; font-size:14px;'>
        نظام تتبع أسعار المنتجات الكهربائية — Dashboard v2.0
    </div>
""", unsafe_allow_html=True)
