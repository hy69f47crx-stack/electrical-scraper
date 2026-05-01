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
    --bg:       #f1f5f9;
    --surface:  #ffffff;
    --border:   #e2e8f0;
    --blue:     #2563eb;
    --blue-l:   #dbeafe;
    --blue-d:   #1d4ed8;
    --teal:     #0f766e;
    --teal-l:   #ccfbf1;
    --violet:   #7c3aed;
    --violet-l: #ede9fe;
    --amber:    #b45309;
    --amber-l:  #fef3c7;
    --red:      #dc2626;
    --t1:       #0f172a;
    --t2:       #475569;
    --t3:       #94a3b8;
    --r:        10px;
    --r-lg:     16px;
    --sh:       0 1px 3px rgba(15,23,42,.07), 0 1px 2px rgba(15,23,42,.04);
    --sh-md:    0 4px 12px rgba(15,23,42,.08), 0 2px 4px rgba(15,23,42,.05);
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
    background: var(--bg) !important;
    color: var(--t1);
}
.block-container {
    padding: 1.25rem 2rem 2rem !important;
    max-width: 1400px;
}

/* ══════════════════════════
   SIDEBAR — dark navy
══════════════════════════ */
section[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-left: none !important;
    width: 230px !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}
/* all text in sidebar */
section[data-testid="stSidebar"] *:not(button) {
    color: #cbd5e1 !important;
    font-family: 'Cairo', sans-serif !important;
}
section[data-testid="stSidebar"] strong,
section[data-testid="stSidebar"] b {
    color: #f1f5f9 !important;
}
/* dividers */
section[data-testid="stSidebar"] hr {
    border-color: #1e293b !important;
    margin: 6px 0 !important;
}
/* metric labels */
section[data-testid="stSidebar"] [data-testid="stMetricLabel"] * {
    color: #94a3b8 !important;
    font-size: 0.72rem !important;
}
section[data-testid="stSidebar"] [data-testid="stMetricValue"] * {
    color: #f1f5f9 !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
}
/* radio — nav links */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 2px !important;
}
section[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 8px 14px !important;
    cursor: pointer !important;
    transition: background .15s !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,.07) !important;
}
section[data-testid="stSidebar"] .stRadio label[data-checked="true"],
section[data-testid="stSidebar"] .stRadio input:checked + div {
    background: rgba(37,99,235,.25) !important;
    border-right: 3px solid #2563eb !important;
}
section[data-testid="stSidebar"] .stRadio input {
    display: none !important;
}
/* sidebar buttons */
section[data-testid="stSidebar"] .stButton button {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
    font-family: 'Cairo', sans-serif !important;
    font-size: 0.85rem !important;
    padding: 6px 12px !important;
    transition: background .15s !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #334155 !important;
    border-color: #475569 !important;
}
section[data-testid="stSidebar"] .stButton [data-testid="baseButton-primary"] {
    background: #1d4ed8 !important;
    border-color: #2563eb !important;
}
section[data-testid="stSidebar"] .stButton [data-testid="baseButton-primary"]:hover {
    background: #2563eb !important;
}
/* caption */
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #64748b !important;
    font-size: 0.74rem !important;
}

/* ══════════════════════════
   PAGE HEADER
══════════════════════════ */
.ph {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: 28px 36px;
    margin-bottom: 24px;
    box-shadow: var(--sh);
    display: flex;
    align-items: center;
    gap: 20px;
}
.ph-icon {
    font-size: 2.4rem;
    line-height: 1;
    flex-shrink: 0;
}
.ph-text h1 {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--t1);
    margin: 0 0 4px;
    letter-spacing: -.02em;
}
.ph-text p {
    font-size: 0.88rem;
    color: var(--t2);
    margin: 0;
}
.ph-badge {
    margin-right: auto;
    background: var(--blue-l);
    color: var(--blue-d);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    font-weight: 600;
    white-space: nowrap;
}

/* ══════════════════════════
   KPI CARDS
══════════════════════════ */
.kpi {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 18px 16px 16px;
    box-shadow: var(--sh);
    display: flex;
    align-items: center;
    gap: 14px;
    transition: box-shadow .18s, transform .18s;
}
.kpi:hover { box-shadow: var(--sh-md); transform: translateY(-2px); }
.kpi-icon-box {
    width: 44px; height: 44px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
}
.kpi-icon-box.blue   { background: var(--blue-l); }
.kpi-icon-box.teal   { background: var(--teal-l); }
.kpi-icon-box.violet { background: var(--violet-l); }
.kpi-icon-box.amber  { background: var(--amber-l); }
.kpi-body { flex: 1; min-width: 0; }
.kpi-val   { font-size: 1.7rem; font-weight: 700; color: var(--t1); line-height: 1; }
.kpi-lbl   { font-size: 0.78rem; color: var(--t2); margin-top: 3px; }

/* ══════════════════════════
   SECTION HEADER
══════════════════════════ */
.sec {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 24px 0 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}
.sec-icon { font-size: 1.1rem; }
.sec-title { font-size: 1.05rem; font-weight: 700; color: var(--t1); }
.sec-badge {
    margin-right: auto;
    background: var(--violet-l);
    color: var(--violet);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.74rem;
    font-weight: 700;
}

/* ══════════════════════════
   DEAL ROW
══════════════════════════ */
.deal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 12px 16px;
    margin-bottom: 8px;
    box-shadow: var(--sh);
    display: flex;
    align-items: center;
    gap: 12px;
    transition: box-shadow .15s;
}
.deal:hover { box-shadow: var(--sh-md); }
.deal-num {
    width: 26px; height: 26px;
    border-radius: 8px;
    background: var(--blue-l);
    color: var(--blue-d);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.78rem; font-weight: 700;
    flex-shrink: 0;
}
.deal-num.n1 { background: #fef3c7; color: #92400e; }
.deal-num.n2 { background: #f1f5f9; color: #475569; }
.deal-num.n3 { background: #fff7ed; color: #9a3412; }
.deal-info { flex: 1; min-width: 0; }
.deal-name  { font-weight: 600; font-size: 0.9rem; color: var(--t1); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.deal-store { font-size: 0.78rem; color: var(--t2); margin-top: 2px; }
.deal-right { text-align: left; flex-shrink: 0; }
.deal-price { font-weight: 700; color: var(--blue); font-size: 0.95rem; }
.deal-save  { display: inline-block; background: var(--teal-l); color: var(--teal); border-radius: 20px; padding: 1px 8px; font-size: 0.73rem; font-weight: 700; margin-top: 2px; }

/* ══════════════════════════
   WORK CARD
══════════════════════════ */
.wc {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 14px 16px;
    margin-bottom: 8px;
    box-shadow: var(--sh);
    border-right: 3px solid var(--violet);
    transition: box-shadow .15s;
}
.wc:hover { box-shadow: var(--sh-md); }
.wc-cat  { display: inline-block; background: var(--violet-l); color: var(--violet); border-radius: 20px; padding: 1px 10px; font-size: 0.73rem; font-weight: 700; }
.wc-desc { font-weight: 600; font-size: 0.92rem; color: var(--t1); margin: 6px 0 4px; line-height: 1.5; }
.wc-meta { font-size: 0.82rem; color: var(--t2); display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.wc-meta .p { color: var(--teal); font-weight: 600; }
.wc-meta .s { background: var(--blue-l); color: var(--blue-d); border-radius: 20px; padding: 1px 9px; font-size: 0.73rem; font-weight: 600; }

/* ══════════════════════════
   PAGE TITLE (inner pages)
══════════════════════════ */
.pt  { font-size: 1.35rem; font-weight: 700; color: var(--t1); margin-bottom: 2px; }
.ps  { font-size: 0.85rem; color: var(--t2); margin-bottom: 20px; }

/* ══════════════════════════
   STORES TABLE
══════════════════════════ */
.store-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
    gap: 10px;
    margin-top: 4px;
}
.store-chip {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 12px 14px;
    box-shadow: var(--sh);
    text-align: center;
}
.store-chip .sc-name { font-weight: 700; font-size: 0.9rem; color: var(--t1); }
.store-chip .sc-count { font-size: 0.78rem; color: var(--t2); margin-top: 3px; }
.store-chip .sc-num { font-size: 1.4rem; font-weight: 700; color: var(--blue); }
</style>
""", unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────
# DATA LOADING
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
    except (FileNotFoundError, ValueError):
        return []


@st.cache_data(ttl=300)
def load_history():
    try:
        with open(BASE_DIR / "price_history.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            return pd.DataFrame(columns=["name", "price", "store", "timestamp"])
        df = pd.DataFrame(data)
        if "price" not in df.columns or "timestamp" not in df.columns:
            return pd.DataFrame(columns=["name", "price", "store", "timestamp"])
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        return df.dropna(subset=["price", "timestamp"])
    except (FileNotFoundError, ValueError):
        return pd.DataFrame(columns=["name", "price", "store", "timestamp"])


@st.cache_data(ttl=300)
def load_work_descriptions():
    try:
        with open(BASE_DIR / "work_descriptions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def reload_all():
    load_products.clear()
    load_groups.clear()
    load_history.clear()
    load_work_descriptions.clear()


# ───────────────────────────────────────────────────────────────
# ACTIONS
# ───────────────────────────────────────────────────────────────
def run_update(run_ai: bool = False):
    steps = [BASE_DIR / "scraper.py", BASE_DIR / "matcher.py"]
    if run_ai:
        steps.append(BASE_DIR / "ai_agent.py")
    label = "جاري التحديث" + (" + AI" if run_ai else "") + " ..."
    with st.spinner(label):
        try:
            for script in steps:
                subprocess.run([sys.executable, str(script)], timeout=600, check=True, capture_output=True)
            reload_all()
            st.success("✅ تم التحديث بنجاح")
            st.rerun()
        except subprocess.CalledProcessError as e:
            st.error(f"فشل: {e.stderr.decode() if e.stderr else str(e)}")
        except subprocess.TimeoutExpired:
            st.error("انتهت المهلة")


def run_ai_only():
    with st.spinner("عميل AI يحلل المنتجات ..."):
        try:
            subprocess.run([sys.executable, str(BASE_DIR / "ai_agent.py")], timeout=600, check=True, capture_output=True)
            reload_all()
            st.success("✅ تم توليد التوصيف")
            st.rerun()
        except subprocess.CalledProcessError as e:
            st.error(f"فشل AI: {e.stderr.decode() if e.stderr else str(e)}")
        except subprocess.TimeoutExpired:
            st.error("انتهت المهلة")


# ───────────────────────────────────────────────────────────────
# SCHEDULER
# ───────────────────────────────────────────────────────────────
if "scheduler_started" not in st.session_state:
    try:
        from scheduler import start_scheduler
        st.session_state["scheduler"] = start_scheduler()
        st.session_state["scheduler_started"] = True
    except Exception:
        st.session_state["scheduler_started"] = False


# ───────────────────────────────────────────────────────────────
# LOAD DATA
# ───────────────────────────────────────────────────────────────
df      = load_products()
groups  = load_groups()
history_df = load_history()
work_data  = load_work_descriptions()

n_products  = len(df)
n_stores    = df["store"].nunique() if not df.empty else 0
n_groups    = len(groups)
n_ai        = len(work_data.get("work_items", []))
avg_saving  = round(sum(g.get("savings_pct", 0) for g in groups) / len(groups), 1) if groups else 0
sched_ok    = st.session_state.get("scheduler_started", False)


# ───────────────────────────────────────────────────────────────
# SIDEBAR
# ───────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="padding:20px 16px 14px;border-bottom:1px solid #1e293b">
        <div style="font-size:1.6rem;line-height:1;margin-bottom:6px">⚡</div>
        <div style="font-size:1rem;font-weight:700;color:#f1f5f9">مقارنة الأسعار</div>
        <div style="font-size:0.75rem;color:#64748b;margin-top:2px">الكويت · الكهرباء</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown("<div style='padding:10px 8px 6px'>", unsafe_allow_html=True)
    page = st.radio(
        "nav",
        ["🏠  الرئيسية", "📦  المنتجات", "⚖️  مقارنة الأسعار",
         "🏆  أفضل العروض", "🤖  توصيف الأعمال", "📈  تاريخ الأسعار", "📊  الرسوم البيانية"],
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # Actions
    st.markdown("<div style='padding:0 8px'>", unsafe_allow_html=True)
    if st.button("🔄  تحديث البيانات", use_container_width=True):
        run_update(run_ai=False)
    if st.button("🤖  تحديث + توصيف AI", use_container_width=True, type="primary"):
        run_update(run_ai=True)
    if st.button("♻️  مسح الكاش", use_container_width=True):
        reload_all(); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # Stats grid
    c1, c2 = st.columns(2)
    with c1:
        st.metric("المنتجات",  f"{n_products:,}")
        st.metric("التوصيف AI", n_ai)
    with c2:
        st.metric("المتاجر",   n_stores)
        st.metric("المطابقة",  n_groups)

    st.divider()

    # Status
    st.caption(f"الجدول التلقائي: {'✅ يعمل' if sched_ok else '⚠️ متوقف'}")
    if not df.empty and "timestamp" in df.columns:
        st.caption(f"آخر جلب: {df['timestamp'].max()}")
    if work_data.get("generated_at"):
        try:
            gd = datetime.fromisoformat(work_data["generated_at"]).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            gd = work_data["generated_at"]
        st.caption(f"آخر توليد AI: {gd}")


# ───────────────────────────────────────────────────────────────
# PAGE: الرئيسية
# ───────────────────────────────────────────────────────────────
if page == "🏠  الرئيسية":

    st.markdown(f"""
    <div class="ph">
        <div class="ph-icon">⚡</div>
        <div class="ph-text">
            <h1>مقارنة الأسعار الكهربائية</h1>
            <p>منصة ذكية لمتابعة أسعار المتاجر الكهربائية الكويتية مع توصيف أعمال بالذكاء الاصطناعي</p>
        </div>
        <div class="ph-badge">🇰🇼 الكويت</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.warning(f"⚠️ لا توجد بيانات. الملف المتوقع: `{BASE_DIR / 'products_all.json'}` — اضغط **🔄 تحديث البيانات** من الشريط الجانبي.")

    # KPI row
    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        (k1, "📦", "blue",   f"{n_products:,}", "إجمالي المنتجات"),
        (k2, "🏪", "teal",   n_stores,          "عدد المتاجر"),
        (k3, "⚖️", "blue",   n_groups,          "منتجات مقارنة"),
        (k4, "💰", "amber",  f"{avg_saving}%",  "متوسط التوفير"),
        (k5, "🤖", "violet", n_ai,              "بنود التوصيف"),
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

    # Two columns layout
    left, right = st.columns([1.1, 1], gap="large")

    with left:
        if groups:
            st.markdown('<div class="sec"><span class="sec-icon">🏆</span><span class="sec-title">أبرز العروض اليوم</span></div>', unsafe_allow_html=True)
            top5 = sorted(groups, key=lambda g: g.get("savings_pct", 0), reverse=True)[:5]
            num_cls = ["n1", "n2", "n3", "", ""]
            for i, g in enumerate(top5):
                nc = num_cls[i] if i < 3 else ""
                st.markdown(f"""
                <div class="deal">
                    <div class="deal-num {nc}">{i+1}</div>
                    <div class="deal-info">
                        <div class="deal-name">{g['canonical_name']}</div>
                        <div class="deal-store">🏪 {g['best_store']}</div>
                    </div>
                    <div class="deal-right">
                        <div class="deal-price">{g['best_price']} KD</div>
                        <div class="deal-save">وفّر {g['savings_pct']}%</div>
                    </div>
                </div>""", unsafe_allow_html=True)

    with right:
        if not df.empty:
            st.markdown('<div class="sec"><span class="sec-icon">🏪</span><span class="sec-title">المتاجر المتاحة</span></div>', unsafe_allow_html=True)
            sc = df.groupby("store").size().reset_index(name="n")
            html_chips = '<div class="store-grid">'
            for _, row in sc.iterrows():
                html_chips += f"""
                <div class="store-chip">
                    <div class="sc-num">{row['n']}</div>
                    <div class="sc-name">{row['store']}</div>
                    <div class="sc-count">منتج</div>
                </div>"""
            html_chips += "</div>"
            st.markdown(html_chips, unsafe_allow_html=True)

    # AI preview
    if work_data.get("work_items"):
        st.markdown('<div class="sec"><span class="sec-icon">🤖</span><span class="sec-title">أبرز بنود التوصيف</span><span class="sec-badge">Claude AI</span></div>', unsafe_allow_html=True)
        for item in work_data["work_items"][:4]:
            st.markdown(f"""
            <div class="wc">
                <span class="wc-cat">{item.get('category','')}</span>
                <div class="wc-desc">{item.get('description','')}</div>
                <div class="wc-meta">
                    <span>أدنى: <span class="p">{item.get('min_price','—')} KD</span></span>
                    <span>متوسط: <span class="p">{item.get('avg_price','—')} KD</span></span>
                    <span>أعلى: <span class="p">{item.get('max_price','—')} KD</span></span>
                    <span class="s">🏪 {item.get('best_store','—')}</span>
                </div>
            </div>""", unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────
# PAGE: المنتجات
# ───────────────────────────────────────────────────────────────
elif page == "📦  المنتجات":
    st.markdown('<div class="pt">📦 قائمة المنتجات</div><div class="ps">تصفح وابحث في جميع المنتجات المجلوبة من المتاجر الكهربائية</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات. اضغط تحديث البيانات من الشريط الجانبي.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            search = st.text_input("🔍 بحث باسم المنتج")
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

        st.caption(f"يُعرض {len(filt):,} منتج")
        cols = [c for c in ["name", "price", "store", "url", "timestamp"] if c in filt.columns]
        labels = {"name": "المنتج", "price": "السعر (KD)", "store": "المتجر", "url": "رابط", "timestamp": "وقت الجلب"}
        st.dataframe(filt[cols].rename(columns=labels), use_container_width=True, hide_index=True)
        st.download_button("⬇️ تحميل CSV", filt.to_csv(index=False).encode("utf-8-sig"), "products.csv", "text/csv")


# ───────────────────────────────────────────────────────────────
# PAGE: مقارنة الأسعار
# ───────────────────────────────────────────────────────────────
elif page == "⚖️  مقارنة الأسعار":
    st.markdown('<div class="pt">⚖️ مقارنة الأسعار بين المتاجر</div><div class="ps">منتجات متطابقة من متاجر مختلفة — الأرخص مظلل بالأخضر</div>', unsafe_allow_html=True)

    if not groups:
        st.warning("لا توجد بيانات مقارنة. شغّل التحديث أولاً.")
    else:
        q = st.text_input("🔍 ابحث عن منتج")
        filtered_groups = [g for g in groups if not q or q.lower() in g["canonical_name"].lower()]
        st.caption(f"{len(filtered_groups)} منتج مطابق")

        for g in filtered_groups[:50]:
            with st.expander(f"📦 {g['canonical_name']}  —  {g['best_price']} KD ({g['best_store']})  |  وفّر {g['savings_pct']}%"):
                rows = []
                for p in g["products"]:
                    rows.append({
                        "المتجر": p["store"],
                        "المنتج": p["name"],
                        "السعر (KD)": p["price"],
                        "الرابط": p.get("url", ""),
                        "": "✅ الأرخص" if p["price"] == g["best_price"] else "",
                    })
                cdf = pd.DataFrame(rows)
                def cr(row):
                    return (["background-color:#d1fae5"] * len(row) if row.get("") == "✅ الأرخص" else [""] * len(row))
                st.dataframe(cdf.style.apply(cr, axis=1), use_container_width=True, hide_index=True)


# ───────────────────────────────────────────────────────────────
# PAGE: أفضل العروض
# ───────────────────────────────────────────────────────────────
elif page == "🏆  أفضل العروض":
    st.markdown('<div class="pt">🏆 أفضل العروض</div><div class="ps">المنتجات ذات أكبر فارق سعري بين المتاجر</div>', unsafe_allow_html=True)

    if not groups:
        st.warning("لا توجد بيانات.")
    else:
        sorted_g = sorted(groups, key=lambda g: g.get("savings_pct", 0), reverse=True)
        min_save = st.slider("الحد الأدنى للتوفير (%)", 0, 100, 10)
        deals = [g for g in sorted_g if g.get("savings_pct", 0) >= min_save]
        st.caption(f"{len(deals)} عرض")

        if deals:
            dd = pd.DataFrame([{
                "المنتج": g["canonical_name"],
                "أفضل سعر (KD)": g["best_price"],
                "أغلى سعر (KD)": g["worst_price"],
                "أفضل متجر": g["best_store"],
                "التوفير": f"{g['savings_pct']}%",
            } for g in deals[:100]])
            st.dataframe(dd, use_container_width=True, hide_index=True)
            st.download_button("⬇️ CSV", dd.to_csv(index=False).encode("utf-8-sig"), "best_deals.csv", "text/csv")

            st.markdown("---")
            st.markdown('<div class="pt" style="font-size:1rem">أفضل 20 عرضاً</div>', unsafe_allow_html=True)
            cd = pd.DataFrame([{"المنتج": g["canonical_name"][:35], "توفير %": g["savings_pct"]} for g in deals[:20]])
            bar = (
                alt.Chart(cd).mark_bar(color="#0f766e", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X("توفير %:Q", title="نسبة التوفير %"),
                    y=alt.Y("المنتج:N", sort="-x", title=""),
                    tooltip=["المنتج", "توفير %"],
                ).properties(height=480)
            )
            st.altair_chart(bar, use_container_width=True)


# ───────────────────────────────────────────────────────────────
# PAGE: توصيف الأعمال
# ───────────────────────────────────────────────────────────────
elif page == "🤖  توصيف الأعمال":
    st.markdown('<div class="pt">🤖 توصيف الأعمال الكهربائية</div><div class="ps">بنود توصيف أعمال الكهرباء المولّدة بالذكاء الاصطناعي بناءً على أسعار السوق الكويتي</div>', unsafe_allow_html=True)

    if not work_data or not work_data.get("work_items"):
        st.info("لم يتم توليد التوصيف بعد. تأكد من وجود ANTHROPIC_API_KEY ثم اضغط الزر.")
        if st.button("🚀 توليد توصيف الأعمال الآن", type="primary"):
            run_ai_only()
    else:
        wi   = work_data["work_items"]
        cats = work_data.get("categories_summary", {})
        pa   = work_data.get("products_analyzed", 0)

        k1, k2, k3 = st.columns(3)
        for col, icon, color, val, lbl in [
            (k1, "📋", "blue",   len(wi),   "بنود التوصيف"),
            (k2, "📂", "teal",   len(cats), "فئات العمل"),
            (k3, "📦", "violet", f"{pa:,}", "منتجات حُللت"),
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

        if work_data.get("generated_at"):
            try:
                gs = datetime.fromisoformat(work_data["generated_at"]).strftime("%Y-%m-%d %H:%M")
            except ValueError:
                gs = work_data["generated_at"]
            st.caption(f"تاريخ التوليد: {gs}")

        st.markdown("")

        cf1, cf2, cf3 = st.columns(3)
        with cf1:
            sw = st.text_input("🔍 بحث في التوصيف")
        with cf2:
            sc = st.selectbox("📂 الفئة", ["الكل"] + sorted(cats.keys()))
        with cf3:
            ss = st.selectbox("🏪 أفضل متجر", ["الكل"] + sorted({i.get("best_store","") for i in wi if i.get("best_store")}))

        fi = wi
        if sw:
            fi = [i for i in fi if sw.lower() in i.get("description","").lower() or sw.lower() in i.get("category","").lower()]
        if sc != "الكل":
            fi = [i for i in fi if i.get("category") == sc]
        if ss != "الكل":
            fi = [i for i in fi if i.get("best_store") == ss]

        st.caption(f"يُعرض {len(fi)} بند")

        if fi:
            td = pd.DataFrame([{
                "رقم": i.get("item_no", n + 1),
                "وصف العمل": i.get("description", ""),
                "الوحدة": i.get("unit", ""),
                "أدنى (KD)": i.get("min_price", ""),
                "متوسط (KD)": i.get("avg_price", ""),
                "أعلى (KD)": i.get("max_price", ""),
                "أفضل متجر": i.get("best_store", ""),
                "الفئة": i.get("category", ""),
            } for n, i in enumerate(fi)])
            st.dataframe(td, use_container_width=True, hide_index=True)
            st.download_button("⬇️ تحميل CSV", td.to_csv(index=False).encode("utf-8-sig"), "work_descriptions.csv", "text/csv")

        if cats:
            st.markdown("---")
            st.markdown('<div class="pt" style="font-size:1rem">توزيع الفئات</div>', unsafe_allow_html=True)
            cat_df = pd.DataFrame([{"الفئة": k, "عدد البنود": v} for k, v in cats.items()]).sort_values("عدد البنود", ascending=False)
            cc = (
                alt.Chart(cat_df).mark_bar(color="#7c3aed", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X("عدد البنود:Q", title=""),
                    y=alt.Y("الفئة:N", sort="-x", title=""),
                    tooltip=["الفئة", "عدد البنود"],
                ).properties(height=320)
            )
            st.altair_chart(cc, use_container_width=True)

        st.markdown("---")
        if st.button("🔄 إعادة التوليد"):
            run_ai_only()


# ───────────────────────────────────────────────────────────────
# PAGE: تاريخ الأسعار
# ───────────────────────────────────────────────────────────────
elif page == "📈  تاريخ الأسعار":
    st.markdown('<div class="pt">📈 تاريخ الأسعار</div><div class="ps">تتبع تغير سعر أي منتج عبر الزمن ومقارنته بين المتاجر</div>', unsafe_allow_html=True)

    if history_df.empty:
        st.info("لا توجد بيانات تاريخية بعد. ستُجمع تلقائياً عند كل تحديث.")
    else:
        sel = st.selectbox("اختر منتجاً", sorted(history_df["name"].unique().tolist()))
        if sel:
            ph = history_df[history_df["name"] == sel].sort_values("timestamp")
            line = (
                alt.Chart(ph).mark_line(point=True, strokeWidth=2)
                .encode(
                    x=alt.X("timestamp:T", title="التاريخ"),
                    y=alt.Y("price:Q", title="السعر (KD)"),
                    color=alt.Color("store:N", title="المتجر"),
                    tooltip=["store", "price", "timestamp"],
                ).properties(height=380, title=sel)
            )
            st.altair_chart(line, use_container_width=True)
            sh = ph[["timestamp", "store", "price"]].rename(columns={"timestamp": "التاريخ", "store": "المتجر", "price": "السعر (KD)"})
            st.dataframe(sh, use_container_width=True, hide_index=True)


# ───────────────────────────────────────────────────────────────
# PAGE: الرسوم البيانية
# ───────────────────────────────────────────────────────────────
elif page == "📊  الرسوم البيانية":
    st.markdown('<div class="pt">📊 الرسوم البيانية</div><div class="ps">تحليل بصري شامل للأسعار والمتاجر</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات.")
    else:
        BLUE   = "#2563eb"
        TEAL   = "#0f766e"
        VIOLET = "#7c3aed"
        AMBER  = "#b45309"

        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.markdown('<div class="sec"><span class="sec-icon">📊</span><span class="sec-title">توزيع الأسعار</span></div>', unsafe_allow_html=True)
            hist = (
                alt.Chart(df).mark_bar(color=BLUE, opacity=.8, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(alt.X("price:Q", bin=alt.Bin(maxbins=35), title="السعر (KD)"), alt.Y("count()", title="عدد المنتجات"))
                .properties(height=260)
            )
            st.altair_chart(hist, use_container_width=True)

        with r1c2:
            st.markdown('<div class="sec"><span class="sec-icon">🏪</span><span class="sec-title">متوسط السعر لكل متجر</span></div>', unsafe_allow_html=True)
            avg_df = df.groupby("store")["price"].mean().reset_index()
            ab = (
                alt.Chart(avg_df).mark_bar(color=TEAL, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(x=alt.X("store:N", title=""), y=alt.Y("price:Q", title="متوسط السعر (KD)"), tooltip=["store", "price"])
                .properties(height=260)
            )
            st.altair_chart(ab, use_container_width=True)

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.markdown('<div class="sec"><span class="sec-icon">💰</span><span class="sec-title">أرخص 20 منتج</span></div>', unsafe_allow_html=True)
            top20 = df.sort_values("price").head(20)
            hb = (
                alt.Chart(top20).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    x=alt.X("price:Q", title="السعر (KD)"),
                    y=alt.Y("name:N", sort="x", title=""),
                    color=alt.Color("store:N", title="المتجر", scale=alt.Scale(scheme="tableau10")),
                    tooltip=["name", "price", "store"],
                ).properties(height=460)
            )
            st.altair_chart(hb, use_container_width=True)

        with r2c2:
            st.markdown('<div class="sec"><span class="sec-icon">📦</span><span class="sec-title">توزيع الأسعار (Box Plot)</span></div>', unsafe_allow_html=True)
            box = (
                alt.Chart(df).mark_boxplot(color=VIOLET)
                .encode(x=alt.X("store:N", title=""), y=alt.Y("price:Q", title="السعر (KD)"), tooltip=["store", "price"])
                .properties(height=460)
            )
            st.altair_chart(box, use_container_width=True)

        st.markdown('<div class="sec"><span class="sec-icon">📏</span><span class="sec-title">نطاق الأسعار لكل متجر</span></div>', unsafe_allow_html=True)
        rdf = df.groupby("store")["price"].agg(["min", "max"]).reset_index()
        rc = (
            alt.Chart(rdf).mark_rule(strokeWidth=5, color=AMBER)
            .encode(x="store:N", y="min:Q", y2="max:Q", tooltip=["store", "min", "max"])
            .properties(height=280)
        )
        st.altair_chart(rc, use_container_width=True)
