import streamlit as st
import pandas as pd
import altair as alt
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="مقارنة الأسعار الكهربائية - الكويت",
    page_icon="⚡",
    layout="wide",
)

# ───────────────────────────────────────────────────────────────
# DESIGN SYSTEM
# ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;900&display=swap');

:root {
    --bg:       #0f172a;
    --surface:  #1a2742;
    --surface2: #253558;
    --border:   #334155;
    --blue:     #3b82f6;
    --blue-l:   #60a5fa;
    --blue-d:   #1d4ed8;
    --teal:     #14b8a6;
    --teal-l:   #2dd4bf;
    --violet:   #a855f7;
    --violet-l: #d8b4fe;
    --amber:    #fbbf24;
    --amber-d:  #b45309;
    --green:    #10b981;
    --red:      #ef4444;
    --t1:       #f1f5f9;
    --t2:       #cbd5e1;
    --t3:       #94a3b8;
    --r:        10px;
    --r-lg:     16px;
    --sh:       0 4px 16px rgba(0,0,0,.4);
    --sh-md:    0 2px 8px rgba(0,0,0,.3);
}

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
    background: var(--bg) !important;
    color: var(--t1);
}

.block-container {
    padding: 1.5rem 2rem 2rem !important;
    max-width: 1400px;
    background: var(--bg) !important;
}

/* ══════════════════════════
   SIDEBAR — DARK MODERN
══════════════════════════ */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-left: 2px solid var(--blue) !important;
}

section[data-testid="stSidebar"] * {
    color: var(--t1) !important;
    font-family: 'Cairo', sans-serif !important;
}

section[data-testid="stSidebar"] strong,
section[data-testid="stSidebar"] b {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] hr {
    border-color: var(--border) !important;
    margin: 8px 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stMetricLabel"] * {
    color: var(--t3) !important;
    font-size: 0.7rem !important;
}

section[data-testid="stSidebar"] [data-testid="stMetricValue"] * {
    color: var(--blue-l) !important;
    font-size: 1.25rem !important;
    font-weight: 700 !important;
}

/* Radio Navigation */
section[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    cursor: pointer !important;
    transition: background .2s !important;
    color: var(--t2) !important;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(59,130,246,.15) !important;
    color: var(--blue-l) !important;
}

section[data-testid="stSidebar"] .stRadio input:checked + label {
    background: rgba(59,130,246,.25) !important;
    color: var(--blue-l) !important;
    border-right: 3px solid var(--blue) !important;
}

/* Sidebar Buttons */
section[data-testid="stSidebar"] .stButton button {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--t1) !important;
    border-radius: 8px !important;
    font-family: 'Cairo', sans-serif !important;
    padding: 8px 12px !important;
    transition: all .2s !important;
    font-size: 0.9rem !important;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: var(--border) !important;
    color: var(--blue-l) !important;
}

/* Primary Button */
section[data-testid="stSidebar"] .stButton [data-testid="baseButton-primary"] {
    background: var(--blue) !important;
    border-color: var(--blue-l) !important;
    color: white !important;
}

section[data-testid="stSidebar"] .stButton [data-testid="baseButton-primary"]:hover {
    background: var(--blue-l) !important;
}

/* Sidebar Caption */
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: var(--t3) !important;
    font-size: 0.72rem !important;
}

/* ══════════════════════════
   SIDEBAR COLLAPSE BUTTON - HIDDEN
══════════════════════════ */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
button[data-testid="stBaseButton-headerNoPadding"] {
    display: none !important;
}

/* Hide expand here */
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* ══════════════════════════
   PAGE HEADER
══════════════════════════ */
.ph {
    background: linear-gradient(135deg, var(--surface2) 0%, rgba(59,130,246,.1) 100%);
    border: 1px solid rgba(59,130,246,.3);
    border-radius: var(--r-lg);
    padding: 32px 40px;
    margin-bottom: 28px;
    box-shadow: var(--sh);
    display: flex;
    align-items: center;
    gap: 24px;
    position: relative;
    overflow: hidden;
}

.ph::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top right, rgba(59,130,246,.1), transparent);
    pointer-events: none;
}

.ph-icon {
    font-size: 2.8rem;
    line-height: 1;
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}

.ph-text {
    flex: 1;
    position: relative;
    z-index: 1;
}

.ph-text h1 {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--t1);
    margin: 0 0 6px;
    letter-spacing: -.02em;
}

.ph-text p {
    font-size: 0.92rem;
    color: var(--t2);
    margin: 0;
}

.ph-badge {
    margin-right: auto;
    background: rgba(20,184,166,.2);
    color: var(--teal-l);
    border: 1px solid rgba(20,184,166,.3);
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 0.8rem;
    font-weight: 700;
    white-space: nowrap;
    position: relative;
    z-index: 1;
}

/* ══════════════════════════
   KPI CARDS
══════════════════════════ */
.kpi {
    background: linear-gradient(135deg, var(--surface2) 0%, rgba(59,130,246,.05) 100%);
    border: 1px solid rgba(59,130,246,.2);
    border-radius: var(--r);
    padding: 20px 16px;
    box-shadow: var(--sh-md);
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all .2s;
}

.kpi:hover {
    box-shadow: var(--sh);
    border-color: rgba(59,130,246,.4);
    background: linear-gradient(135deg, var(--surface2) 0%, rgba(59,130,246,.15) 100%);
}

.kpi-icon-box {
    width: 48px;
    height: 48px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
}

.kpi-icon-box.blue   { background: rgba(59,130,246,.25); }
.kpi-icon-box.teal   { background: rgba(20,184,166,.25); }
.kpi-icon-box.violet { background: rgba(168,85,247,.25); }
.kpi-icon-box.amber  { background: rgba(251,191,36,.25); }

.kpi-body {
    flex: 1;
}

.kpi-val {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--t1);
    line-height: 1;
}

.kpi-lbl {
    font-size: 0.8rem;
    color: var(--t3);
    margin-top: 4px;
}

/* ══════════════════════════
   SECTION HEADER
══════════════════════════ */
.sec {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(59,130,246,.2);
}

.sec-icon {
    font-size: 1.2rem;
}

.sec-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--t1);
}

.sec-badge {
    margin-right: auto;
    background: rgba(168,85,247,.2);
    color: var(--violet-l);
    border: 1px solid rgba(168,85,247,.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.76rem;
    font-weight: 700;
}

/* ══════════════════════════
   DEAL ROW
══════════════════════════ */
.deal {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 14px 16px;
    margin-bottom: 10px;
    box-shadow: var(--sh-md);
    display: flex;
    align-items: center;
    gap: 14px;
    transition: all .2s;
}

.deal:hover {
    box-shadow: var(--sh);
    border-color: var(--blue);
}

.deal-num {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: rgba(59,130,246,.25);
    color: var(--blue-l);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    flex-shrink: 0;
}

.deal-num.n1 { background: rgba(251,191,36,.25); color: var(--amber); }
.deal-num.n2 { background: rgba(148,163,184,.15); color: var(--t2); }
.deal-num.n3 { background: rgba(217,119,6,.25); color: #f97316; }

.deal-info {
    flex: 1;
}

.deal-name {
    font-weight: 600;
    font-size: 0.92rem;
    color: var(--t1);
}

.deal-store {
    font-size: 0.8rem;
    color: var(--t3);
    margin-top: 2px;
}

.deal-right {
    text-align: left;
    flex-shrink: 0;
}

.deal-price {
    font-weight: 700;
    color: var(--blue-l);
    font-size: 0.96rem;
}

.deal-save {
    display: inline-block;
    background: rgba(20,184,166,.2);
    color: var(--teal-l);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.74rem;
    font-weight: 700;
    margin-top: 2px;
}

/* ══════════════════════════
   WORK CARD
══════════════════════════ */
.wc {
    background: var(--surface2);
    border: 1px solid rgba(168,85,247,.2);
    border-radius: var(--r);
    padding: 16px 18px;
    margin-bottom: 10px;
    box-shadow: var(--sh-md);
    border-right: 3px solid var(--violet);
    transition: all .2s;
}

.wc:hover {
    box-shadow: var(--sh);
    border-color: rgba(168,85,247,.4);
}

.wc-cat {
    display: inline-block;
    background: rgba(168,85,247,.2);
    color: var(--violet-l);
    border-radius: 20px;
    padding: 3px 11px;
    font-size: 0.75rem;
    font-weight: 700;
}

.wc-desc {
    font-weight: 600;
    font-size: 0.94rem;
    color: var(--t1);
    margin: 8px 0 5px;
    line-height: 1.5;
}

.wc-meta {
    font-size: 0.85rem;
    color: var(--t2);
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.wc-meta .p {
    color: var(--teal-l);
    font-weight: 700;
}

.wc-meta .s {
    background: rgba(59,130,246,.2);
    color: var(--blue-l);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 700;
}

/* ══════════════════════════
   PAGE TITLE
══════════════════════════ */
.pt {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--t1);
    margin-bottom: 3px;
}

.ps {
    font-size: 0.88rem;
    color: var(--t2);
    margin-bottom: 22px;
}

/* ══════════════════════════
   STORE GRID
══════════════════════════ */
.store-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
}

.store-chip {
    background: var(--surface2);
    border: 1px solid rgba(59,130,246,.2);
    border-radius: var(--r);
    padding: 14px 12px;
    box-shadow: var(--sh-md);
    text-align: center;
    transition: all .2s;
}

.store-chip:hover {
    border-color: rgba(59,130,246,.4);
    box-shadow: var(--sh);
}

.store-chip .sc-num {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--blue-l);
}

.store-chip .sc-name {
    font-weight: 700;
    font-size: 0.92rem;
    color: var(--t1);
    margin-top: 4px;
}

.store-chip .sc-count {
    font-size: 0.78rem;
    color: var(--t3);
    margin-top: 2px;
}

/* ══════════════════════════
   DATAFRAME STYLING
══════════════════════════ */
[data-testid="stDataFrame"] {
    background: var(--surface2) !important;
}

[data-testid="stDataFrame"] > div > div > table {
    background: var(--surface2) !important;
}

[data-testid="stDataFrame"] th {
    background: rgba(59,130,246,.15) !important;
    color: var(--blue-l) !important;
    border-color: var(--border) !important;
    font-weight: 700 !important;
    font-family: 'Cairo' !important;
}

[data-testid="stDataFrame"] td {
    color: var(--t1) !important;
    border-color: var(--border) !important;
    font-family: 'Cairo' !important;
}

[data-testid="stDataFrame"] tr:hover td {
    background: rgba(59,130,246,.08) !important;
}

/* Responsive */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem !important;
    }

    .ph {
        padding: 20px 24px;
        gap: 16px;
    }

    .ph h1 {
        font-size: 1.4rem !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────
# DATA & FUNCTIONS
# ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_products():
    try:
        with open(BASE_DIR / "products_all.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        return df.dropna(subset=["price"])
    except (FileNotFoundError, ValueError, KeyError):
        return pd.DataFrame(columns=["name", "price", "store", "url", "timestamp", "currency"])


@st.cache_data(ttl=300)
def load_groups():
    try:
        with open(BASE_DIR / "matched_groups.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


@st.cache_data(ttl=300)
def load_history():
    try:
        with open(BASE_DIR / "price_history.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            return pd.DataFrame(columns=["name", "price", "store", "timestamp"])
        df = pd.DataFrame(data)
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        return df.dropna(subset=["price", "timestamp"])
    except:
        return pd.DataFrame(columns=["name", "price", "store", "timestamp"])


@st.cache_data(ttl=300)
def load_work_descriptions():
    try:
        with open(BASE_DIR / "work_descriptions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def reload_all():
    load_products.clear()
    load_groups.clear()
    load_history.clear()
    load_work_descriptions.clear()


def run_update(run_ai: bool = False):
    steps = [BASE_DIR / "scraper.py", BASE_DIR / "matcher.py"]
    if run_ai:
        steps.append(BASE_DIR / "ai_agent.py")

    with st.spinner("جاري التحديث ..."):
        try:
            for script in steps:
                subprocess.run([sys.executable, str(script)], timeout=600, check=True, capture_output=True)
            reload_all()
            st.success("✅ تم التحديث بنجاح")
            st.rerun()
        except Exception as e:
            st.error(f"❌ فشل: {str(e)[:100]}")


def run_ai_only():
    with st.spinner("عميل AI يعمل ..."):
        try:
            subprocess.run([sys.executable, str(BASE_DIR / "ai_agent.py")], timeout=600, check=True, capture_output=True)
            reload_all()
            st.success("✅ تم التوليد بنجاح")
            st.rerun()
        except Exception as e:
            st.error(f"❌ فشل: {str(e)[:100]}")


# Scheduler
if "scheduler_started" not in st.session_state:
    try:
        from scheduler import start_scheduler
        st.session_state["scheduler"] = start_scheduler()
        st.session_state["scheduler_started"] = True
    except:
        st.session_state["scheduler_started"] = False


# Load data
df = load_products()
groups = load_groups()
history_df = load_history()
work_data = load_work_descriptions()

n_products = len(df)
n_stores = df["store"].nunique() if not df.empty else 0
n_groups = len(groups)
n_ai = len(work_data.get("work_items", []))
avg_saving = round(sum(g.get("savings_pct", 0) for g in groups) / len(groups), 1) if groups else 0
sched_ok = st.session_state.get("scheduler_started", False)


# ───────────────────────────────────────────────────────────────
# SIDEBAR
# ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 0 16px 0;text-align:center">
        <div style="font-size:2rem;margin-bottom:8px">⚡</div>
        <div style="font-size:1.05rem;font-weight:700;color:#f1f5f9">مقارنة الأسعار</div>
        <div style="font-size:0.76rem;color:#94a3b8;margin-top:3px">الكويت الكهربائية</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    page = st.radio(
        "nav",
        ["🏠 الرئيسية", "📦 المنتجات", "📂 الفئات والتفريعات", "⚖️ مقارنة الأسعار",
         "🏆 أفضل العروض", "🤖 توصيف الأعمال", "📈 تاريخ الأسعار", "📊 الرسوم البيانية"],
        label_visibility="collapsed",
    )

    st.divider()

    # Single update menu
    with st.popover("⚙️ تحديث البيانات", use_container_width=True):
        st.markdown("**خيارات التحديث**")
        if st.button("🔄 تحديث البيانات فقط", use_container_width=True):
            run_update(run_ai=False)
        if st.button("🤖 تحديث + توصيف الأعمال", use_container_width=True):
            run_update(run_ai=True)
        if st.button("♻️ مسح الكاش", use_container_width=True):
            reload_all()
            st.rerun()

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.metric("المنتجات", f"{n_products:,}")
        st.metric("التوصيف", n_ai)
    with c2:
        st.metric("المتاجر", n_stores)
        st.metric("المطابقة", n_groups)

    st.divider()
    st.caption(f"🔄 الجدول: {'✅ يعمل' if sched_ok else '⚠️ متوقف'}")
    if not df.empty and "timestamp" in df.columns:
        st.caption(f"📅 آخر: {df['timestamp'].max()}")


# ───────────────────────────────────────────────────────────────
# PAGES
# ───────────────────────────────────────────────────────────────
if page == "🏠 الرئيسية":
    st.markdown(f"""
    <div class="ph">
        <div class="ph-icon">⚡</div>
        <div class="ph-text">
            <h1>مقارنة الأسعار الكهربائية</h1>
            <p>منصة ذكية لمتابعة أسعار المتاجر الكويتية مع توصيف أعمال بالذكاء الاصطناعي</p>
        </div>
        <div class="ph-badge">🇰🇼 الكويت</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.warning("⚠️ لا توجد بيانات — استخدم ⚙️ تحديث البيانات من الشريط الجانبي")

    # KPI Row
    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        (k1, "📦", "blue", f"{n_products:,}", "المنتجات"),
        (k2, "🏪", "teal", n_stores, "المتاجر"),
        (k3, "⚖️", "blue", n_groups, "المطابقة"),
        (k4, "💰", "amber", f"{avg_saving}%", "التوفير"),
        (k5, "🤖", "violet", n_ai, "التوصيف"),
    ]
    for col, icon, color, val, lbl in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-icon-box {color}">{icon}</div>
                <div class="kpi-body">
                    <div class="kpi-val">{val}</div>
                    <div class="kpi-lbl">{lbl}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    # Store chips grid
    if not df.empty:
        st.markdown('<div class="sec"><span class="sec-icon">🏪</span><span class="sec-title">المتاجر</span></div>', unsafe_allow_html=True)
        sc = df.groupby("store").size().reset_index(name="n")
        cols = st.columns(min(3, len(sc)))
        for idx, (_, row) in enumerate(sc.iterrows()):
            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div class="store-chip">
                    <div class="sc-num">{row['n']}</div>
                    <div class="sc-name">{row['store']}</div>
                    <div class="sc-count">منتج</div>
                </div>""", unsafe_allow_html=True)

    if work_data.get("work_items"):
        st.markdown('<div class="sec"><span class="sec-icon">🤖</span><span class="sec-title">توصيف الأعمال</span><span class="sec-badge">Claude AI</span></div>', unsafe_allow_html=True)
        for item in work_data["work_items"][:3]:
            st.markdown(f"""
            <div class="wc">
                <span class="wc-cat">{item.get('category','')}</span>
                <div class="wc-desc">{item.get('description','')[:70]}...</div>
                <div class="wc-meta">
                    <span>📊 <span class="p">{item.get('min_price','—')} KD</span></span>
                    <span class="s">🏪 {item.get('best_store','—')}</span>
                </div>
            </div>""", unsafe_allow_html=True)


elif page == "📦 المنتجات":
    st.markdown('<div class="pt">📦 قائمة المنتجات</div><div class="ps">تصفح وابحث في المنتجات الكهربائية</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            search = st.text_input("🔍 بحث")
        with c2:
            stores = ["الكل"] + sorted(df["store"].unique().tolist())
            sel_store = st.selectbox("🏪 المتجر", stores)
        with c3:
            min_p, max_p = float(df["price"].min()), float(df["price"].max())
            price_range = (min_p, max_p) if min_p == max_p else st.slider("💰 السعر (KD)", min_p, max_p, (min_p, max_p))

        filt = df.copy()
        if search:
            filt = filt[filt["name"].str.contains(search, case=False, na=False)]
        if sel_store != "الكل":
            filt = filt[filt["store"] == sel_store]
        filt = filt[(filt["price"] >= price_range[0]) & (filt["price"] <= price_range[1])]

        st.caption(f"**{len(filt):,}** منتج")
        show = filt[["name", "price", "store"]].copy()
        show.columns = ["المنتج", "السعر (KD)", "المتجر"]
        st.table(show)


elif page == "📂 الفئات والتفريعات":
    st.markdown('<div class="pt">📂 الفئات والتفريعات</div><div class="ps">تصنيف المنتجات حسب الفئات والعلامات التجارية</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات")
    else:
        # Extract categories/brands from product names
        def extract_category(name):
            keywords = {
                "كيبل": "الكيبلات والأسلاك",
                "مفتاح": "المفاتيح والقواطع",
                "مصابيح": "المصابيح والإضاءة",
                "مصباح": "المصابيح والإضاءة",
                "led": "المصابيح والإضاءة",
                "لد": "المصابيح والإضاءة",
                "مقبس": "المقابس والمنافذ",
                "منفذ": "المقابس والمنافذ",
                "ترانس": "المحولات",
                "محول": "المحولات",
                "بطارية": "البطاريات",
                "مولد": "المولدات",
                "مراوح": "المراوح والتهوية",
                "مروحة": "المراوح والتهوية",
                "مكيف": "تكييف الهواء",
                "ثلاجة": "الأجهزة الكهربائية",
                "غسالة": "الأجهزة الكهربائية",
                "سخان": "سخانات المياه",
                "شاحن": "أجهزة الشحن",
            }
            name_lower = name.lower()
            for kw, cat in keywords.items():
                if kw in name_lower:
                    return cat
            return "أخرى"

        df_cat = df.copy()
        df_cat["category"] = df_cat["name"].apply(extract_category)

        # Category stats
        cat_counts = df_cat["category"].value_counts()
        st.markdown('<div class="sec"><span class="sec-icon">📊</span><span class="sec-title">إحصائيات الفئات</span></div>', unsafe_allow_html=True)

        cols = st.columns(min(3, len(cat_counts)))
        for idx, (cat, count) in enumerate(cat_counts.items()):
            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div class="kpi">
                    <div class="kpi-icon-box blue">📦</div>
                    <div class="kpi-body">
                        <div class="kpi-val">{count}</div>
                        <div class="kpi-lbl">{cat}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # Detailed category breakdown
        st.markdown('<div class="sec"><span class="sec-icon">📋</span><span class="sec-title">تفصيل المنتجات</span></div>', unsafe_allow_html=True)

        sel_cat = st.selectbox("اختر فئة", sorted(cat_counts.index.tolist()))
        cat_products = df_cat[df_cat["category"] == sel_cat]

        st.caption(f"**{len(cat_products)}** منتج في فئة: **{sel_cat}**")

        # Detailed breakdown by store
        for store in sorted(cat_products["store"].unique()):
            store_data = cat_products[cat_products["store"] == store]
            with st.expander(f"🏪 {store} ({len(store_data)} منتجات)"):
                show = store_data[["name", "price"]].copy()
                show.columns = ["المنتج", "السعر (KD)"]
                st.table(show)


elif page == "⚖️ مقارنة الأسعار":
    st.markdown('<div class="pt">⚖️ مقارنة الأسعار</div><div class="ps">نفس المنتج من متاجر مختلفة</div>', unsafe_allow_html=True)

    if not groups:
        st.warning("لا توجد بيانات")
    else:
        q = st.text_input("🔍 ابحث")
        filtered_groups = [g for g in groups if not q or q.lower() in g["canonical_name"].lower()]
        st.caption(f"**{len(filtered_groups)}** منتج مطابق")

        for g in filtered_groups[:50]:
            with st.expander(f"📦 {g['canonical_name']} — {g['best_price']} KD | {g['savings_pct']}% توفير"):
                rows = []
                for p in g["products"]:
                    rows.append({
                        "✔": "✅" if p["price"] == g["best_price"] else "",
                        "المتجر": p["store"],
                        "السعر (KD)": p["price"],
                    })
                st.table(pd.DataFrame(rows))


elif page == "🏆 أفضل العروض":
    st.markdown('<div class="pt">🏆 أفضل العروض</div><div class="ps">أكبر فارق سعري بين المتاجر</div>', unsafe_allow_html=True)

    if not groups:
        st.warning("لا توجد بيانات")
    else:
        min_save = st.slider("الحد الأدنى للتوفير (%)", 0, 100, 10)
        deals = [g for g in sorted(groups, key=lambda g: g.get("savings_pct", 0), reverse=True) if g.get("savings_pct", 0) >= min_save]
        st.caption(f"**{len(deals)}** عرض")

        if deals:
            dd = pd.DataFrame([{
                "المنتج": g["canonical_name"][:40],
                "أفضل سعر": f"{g['best_price']} KD",
                "توفير": f"{g['savings_pct']}%",
            } for g in deals[:100]])
            st.table(dd)

            st.markdown("---")
            st.markdown("**أفضل 20 عرضاً**")
            cd = pd.DataFrame([{"المنتج": g["canonical_name"][:30], "توفير %": g["savings_pct"]} for g in deals[:20]])
            bar = (
                alt.Chart(cd).mark_bar(color="#3b82f6", cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
                .encode(
                    x=alt.X("توفير %:Q"),
                    y=alt.Y("المنتج:N", sort="-x"),
                    tooltip=["المنتج", "توفير %"],
                ).properties(height=450)
            )
            st.altair_chart(bar, use_container_width=True)


elif page == "🤖 توصيف الأعمال":
    st.markdown('<div class="pt">🤖 توصيف الأعمال</div><div class="ps">بنود أعمال الكهرباء بالذكاء الاصطناعي</div>', unsafe_allow_html=True)

    if not work_data or not work_data.get("work_items"):
        st.info("لم يتم التوليد بعد — استخدم خيار التحديث + توصيف الأعمال")
        if st.button("🚀 توليد الآن", type="primary"):
            run_ai_only()
    else:
        wi = work_data["work_items"]
        cats = work_data.get("categories_summary", {})

        k1, k2, k3 = st.columns(3)
        for col, icon, color, val, lbl in [
            (k1, "📋", "blue", len(wi), "البنود"),
            (k2, "📂", "teal", len(cats), "الفئات"),
            (k3, "📦", "violet", work_data.get("products_analyzed", 0), "تحليل"),
        ]:
            with col:
                st.markdown(f"""
                <div class="kpi">
                    <div class="kpi-icon-box {color}">{icon}</div>
                    <div class="kpi-body">
                        <div class="kpi-val">{val}</div>
                        <div class="kpi-lbl">{lbl}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("")
        cf1, cf2 = st.columns(2)
        with cf1:
            sw = st.text_input("🔍 بحث")
        with cf2:
            sc = st.selectbox("📂 الفئة", ["الكل"] + sorted(cats.keys()))

        fi = wi
        if sw:
            fi = [i for i in fi if sw.lower() in i.get("description", "").lower()]
        if sc != "الكل":
            fi = [i for i in fi if i.get("category") == sc]

        st.caption(f"**{len(fi)}** بند")
        if fi:
            td = pd.DataFrame([{
                "رقم": i.get("item_no", n+1),
                "الوصف": i.get("description", "")[:50],
                "السعر": f"{i.get('min_price','—')} - {i.get('max_price','—')} KD",
            } for n, i in enumerate(fi)])
            st.table(td)


elif page == "📈 تاريخ الأسعار":
    st.markdown('<div class="pt">📈 تاريخ الأسعار</div><div class="ps">تتبع تغير السعر عبر الزمن</div>', unsafe_allow_html=True)

    if history_df.empty:
        st.info("لا توجد بيانات تاريخية بعد")
    else:
        sel = st.selectbox("اختر منتجاً", sorted(history_df["name"].unique().tolist()))
        if sel:
            ph = history_df[history_df["name"] == sel].sort_values("timestamp")
            line = (
                alt.Chart(ph).mark_line(point=True, strokeWidth=2, color="#3b82f6")
                .encode(
                    x=alt.X("timestamp:T", title="التاريخ"),
                    y=alt.Y("price:Q", title="السعر (KD)"),
                    color=alt.Color("store:N"),
                    tooltip=["store", "price", "timestamp"],
                ).properties(height=350)
            )
            st.altair_chart(line, use_container_width=True)


elif page == "📊 الرسوم البيانية":
    st.markdown('<div class="pt">📊 الرسوم البيانية</div><div class="ps">تحليل بصري للأسعار والمتاجر</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات")
    else:
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.markdown("**توزيع الأسعار**")
            hist = (
                alt.Chart(df).mark_bar(color="#3b82f6", opacity=.8)
                .encode(alt.X("price:Q", bin=alt.Bin(maxbins=35)), alt.Y("count()"))
                .properties(height=300)
            )
            st.altair_chart(hist, use_container_width=True)

        with r1c2:
            st.markdown("**متوسط السعر**")
            avg_df = df.groupby("store")["price"].mean().reset_index()
            ab = (
                alt.Chart(avg_df).mark_bar(color="#14b8a6")
                .encode(x=alt.X("store:N", title=""), y=alt.Y("price:Q"))
                .properties(height=300)
            )
            st.altair_chart(ab, use_container_width=True)
