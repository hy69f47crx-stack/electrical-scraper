import os
import streamlit as st
import pandas as pd
import altair as alt
import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ─────────────────────────────────────────────────────────────────
# CLOUD DETECTION
# ─────────────────────────────────────────────────────────────────
IS_CLOUD = (
    os.environ.get("STREAMLIT_SHARING_MODE") == "1"
    or os.environ.get("IS_STREAMLIT_CLOUD") == "1"
    or "STREAMLIT_SERVER_HEADLESS" in os.environ
    or os.path.exists("/mount/src")
)

# ─────────────────────────────────────────────────────────────────
# API KEY
# ─────────────────────────────────────────────────────────────────
def get_api_key() -> str | None:
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=BASE_DIR / ".env")
    except ImportError:
        pass
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            pass
    return key.strip() if key and key.strip() not in ("", "PUT_YOUR_KEY_HERE") else None


st.set_page_config(
    page_title="مقارنة الأسعار الكهربائية - الكويت",
    page_icon="⚡",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────
# CSS — Light Pastel Theme + Responsive + RTL
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;900&display=swap');

/* ══ Design tokens ══════════════════════════════════════════════ */
:root {
    --bg:       #f5f7fb;
    --surface:  #ffffff;
    --surface2: #f0f4ff;
    --border:   #d4dbe8;
    --blue:     #2563eb;
    --blue-l:   #60a5fa;
    --blue-d:   #1d4ed8;
    --teal:     #0d9488;
    --teal-l:   #2dd4bf;
    --violet:   #7c3aed;
    --amber:    #f59e0b;
    --green:    #16a34a;
    --red:      #dc2626;
    --t1:       #0f172a;
    --t2:       #475569;
    --t3:       #94a3b8;
    --r:        10px;
    --r-lg:     16px;
    --sh:       0 4px 16px rgba(15,23,42,.10), 0 1px 4px rgba(15,23,42,.06);
    --sh-sm:    0 2px 8px  rgba(15,23,42,.08), 0 1px 2px rgba(15,23,42,.04);
}

/* ══ Global ═════════════════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl !important;
    background: var(--bg) !important;
    color: var(--t1) !important;
}
.block-container {
    padding: 1.5rem 2rem 3rem !important;
    max-width: 1400px !important;
    background: var(--bg) !important;
}

/* ══ Sidebar ════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-left: 2px solid var(--blue) !important;
    box-shadow: var(--sh-sm) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--t1) !important;
    font-family: 'Cairo', sans-serif !important;
}
section[data-testid="stSidebar"] hr { border-color: var(--border) !important; margin: 8px 0 !important; }
section[data-testid="stSidebar"] [data-testid="stMetricLabel"] * { color: var(--t3) !important; font-size: 0.7rem !important; }
section[data-testid="stSidebar"] [data-testid="stMetricValue"] * { color: var(--blue) !important; font-size: 1.2rem !important; font-weight: 700 !important; }
section[data-testid="stSidebar"] .stRadio label {
    border-radius: 8px !important; padding: 10px 14px !important;
    cursor: pointer !important; transition: background .15s !important; color: var(--t2) !important;
}
section[data-testid="stSidebar"] .stRadio label:hover { background: rgba(37,99,235,.08) !important; color: var(--blue) !important; }
section[data-testid="stSidebar"] .stRadio input:checked + label {
    background: rgba(37,99,235,.12) !important; color: var(--blue) !important;
    font-weight: 600 !important; border-right: 3px solid var(--blue) !important;
}
section[data-testid="stSidebar"] .stButton button {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    color: var(--t1) !important; border-radius: 8px !important;
    font-family: 'Cairo', sans-serif !important; transition: all .15s !important;
}
section[data-testid="stSidebar"] .stButton button:hover { background: var(--border) !important; color: var(--blue) !important; }
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: var(--t3) !important; font-size: 0.72rem !important; }

/* ══ Hide collapse buttons ══════════════════════════════════════ */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
button[data-testid="stBaseButton-headerNoPadding"],
[role="button"][aria-label="Expand"],
button[aria-label="Expand"],
button[data-testid*="expanderButton"] { display: none !important; }

/* ══ Sidebar toggle button ══════════════════════════════════════ */
.sidebar-toggle {
    position: fixed; top: 16px; right: 16px; z-index: 9999;
    background: var(--blue) !important; border: none !important;
    color: white !important; width: 44px !important; height: 44px !important;
    border-radius: 8px !important; cursor: pointer !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    font-size: 1.4rem !important; box-shadow: var(--sh-sm) !important;
    transition: all .2s !important; padding: 0 !important; line-height: 1 !important;
}
.sidebar-toggle:hover  { background: var(--blue-d) !important; }
.sidebar-toggle:active { transform: scale(0.95); }

/* ══ Page header ════════════════════════════════════════════════ */
.ph {
    background: linear-gradient(135deg, var(--surface2) 0%, rgba(37,99,235,.06) 100%);
    border: 1px solid rgba(37,99,235,.18); border-radius: var(--r-lg);
    padding: 28px 36px; margin-bottom: 24px; box-shadow: var(--sh);
    display: flex; align-items: center; gap: 20px; position: relative; overflow: hidden;
}
.ph::before {
    content: ""; position: absolute; inset: 0;
    background: radial-gradient(circle at top right, rgba(37,99,235,.07), transparent);
    pointer-events: none;
}
.ph-icon { font-size: 2.6rem; line-height: 1; flex-shrink: 0; position: relative; z-index: 1; }
.ph-text { flex: 1; position: relative; z-index: 1; min-width: 0; }
.ph-text h1 { font-size: 1.7rem; font-weight: 700; color: var(--t1); margin: 0 0 5px; letter-spacing: -.02em; }
.ph-text p  { font-size: 0.88rem; color: var(--t2); margin: 0; }
.ph-badge {
    margin-right: auto; flex-shrink: 0;
    background: rgba(13,148,136,.12); color: var(--teal);
    border: 1px solid rgba(13,148,136,.25); border-radius: 20px;
    padding: 5px 14px; font-size: 0.78rem; font-weight: 700;
    white-space: nowrap; position: relative; z-index: 1;
}

/* ══ KPI cards ══════════════════════════════════════════════════ */
.kpi {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r); padding: 18px 14px; box-shadow: var(--sh-sm);
    display: flex; align-items: center; gap: 14px; transition: all .2s;
    height: 100%; min-height: 80px;
}
.kpi:hover { box-shadow: var(--sh); border-color: rgba(37,99,235,.35); transform: translateY(-1px); }
.kpi-icon-box {
    width: 44px; height: 44px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; flex-shrink: 0;
}
.kpi-icon-box.blue   { background: rgba(37,99,235,.12); }
.kpi-icon-box.teal   { background: rgba(13,148,136,.12); }
.kpi-icon-box.violet { background: rgba(124,58,237,.12); }
.kpi-icon-box.amber  { background: rgba(245,158,11,.12); }
.kpi-body { flex: 1; min-width: 0; }
.kpi-val  { font-size: 1.7rem; font-weight: 700; color: var(--t1); line-height: 1; }
.kpi-lbl  { font-size: 0.78rem; color: var(--t3); margin-top: 4px; }

/* ══ Section header ═════════════════════════════════════════════ */
.sec {
    display: flex; align-items: center; gap: 10px;
    margin: 24px 0 14px; padding-bottom: 10px;
    border-bottom: 2px solid rgba(37,99,235,.12);
}
.sec-icon  { font-size: 1.1rem; }
.sec-title { font-size: 1.05rem; font-weight: 700; color: var(--t1); }
.sec-badge {
    margin-right: auto; background: rgba(124,58,237,.10); color: var(--violet);
    border: 1px solid rgba(124,58,237,.2); border-radius: 20px;
    padding: 3px 12px; font-size: 0.74rem; font-weight: 700;
}

/* ══ Work card ══════════════════════════════════════════════════ */
.wc {
    background: var(--surface); border: 1px solid rgba(124,58,237,.15);
    border-right: 3px solid var(--violet); border-radius: var(--r);
    padding: 14px 16px; margin-bottom: 10px; box-shadow: var(--sh-sm); transition: all .2s;
}
.wc:hover { box-shadow: var(--sh); border-color: rgba(124,58,237,.3); }
.wc-cat {
    display: inline-block; background: rgba(124,58,237,.10); color: var(--violet);
    border-radius: 20px; padding: 3px 11px; font-size: 0.73rem; font-weight: 700;
}
.wc-desc { font-weight: 600; font-size: 0.9rem; color: var(--t1); margin: 7px 0 5px; line-height: 1.5; }
.wc-meta { font-size: 0.82rem; color: var(--t2); display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.wc-meta .p { color: var(--teal); font-weight: 700; }
.wc-meta .s {
    background: rgba(37,99,235,.10); color: var(--blue);
    border-radius: 20px; padding: 2px 10px; font-size: 0.73rem; font-weight: 700;
}

/* ══ Page title ═════════════════════════════════════════════════ */
.pt { font-size: 1.45rem; font-weight: 700; color: var(--t1); margin-bottom: 3px; }
.ps { font-size: 0.86rem; color: var(--t2); margin-bottom: 20px; }

/* ══ Store chip ═════════════════════════════════════════════════ */
.store-chip {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r); padding: 14px 10px; box-shadow: var(--sh-sm);
    text-align: center; transition: all .2s;
}
.store-chip:hover { border-color: var(--blue); box-shadow: var(--sh); }
.store-chip .sc-num  { font-size: 1.5rem; font-weight: 700; color: var(--blue); }
.store-chip .sc-name { font-weight: 700; font-size: 0.88rem; color: var(--t1); margin-top: 3px; }
.store-chip .sc-count{ font-size: 0.74rem; color: var(--t3); margin-top: 2px; }

/* ══ Cloud banner ═══════════════════════════════════════════════ */
.cloud-info {
    background: rgba(37,99,235,.06); border: 1px solid rgba(37,99,235,.2);
    border-right: 4px solid var(--blue); border-radius: var(--r);
    padding: 12px 16px; font-size: 0.88rem; color: var(--t2); margin-bottom: 4px;
}
.cloud-info b { color: var(--blue); }

/* ══ Input controls ═════════════════════════════════════════════ */
/* Text inputs */
.stTextInput input, .stSelectbox select {
    font-family: 'Cairo', sans-serif !important;
    font-size: 0.9rem !important;
    border-radius: 8px !important;
    border-color: var(--border) !important;
    background: var(--surface) !important;
    color: var(--t1) !important;
    direction: rtl !important;
}
.stTextInput label, .stSelectbox label, .stSlider label {
    font-family: 'Cairo', sans-serif !important;
    font-size: 0.88rem !important;
    color: var(--t2) !important;
    font-weight: 600 !important;
}
/* Slider — constrain width, prevent overflow */
.stSlider {
    max-width: 100% !important;
    overflow: hidden !important;
    padding: 0 4px !important;
}
.stSlider > div {
    max-width: 100% !important;
}
[data-testid="stSlider"] {
    padding: 4px 2px !important;
    overflow: hidden !important;
}
[data-testid="stSlider"] > div > div {
    overflow: hidden !important;
}
/* Selectbox */
[data-testid="stSelectbox"] {
    max-width: 100% !important;
}
[data-testid="stSelectbox"] > div > div {
    font-family: 'Cairo', sans-serif !important;
    font-size: 0.88rem !important;
    background: var(--surface) !important;
    border-color: var(--border) !important;
    border-radius: 8px !important;
    color: var(--t1) !important;
}
/* Filter row container */
.filter-row {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 16px 18px;
    margin-bottom: 16px;
    box-shadow: var(--sh-sm);
}

/* ══ Dataframe / Table ══════════════════════════════════════════ */
/* Outer wrapper — enable scroll, styled card */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    overflow: hidden !important;
    box-shadow: var(--sh-sm) !important;
    background: var(--surface) !important;
    max-width: 100% !important;
    display: block !important;
}
/* The glide-data-grid canvas wrapper */
[data-testid="stDataFrame"] > div {
    max-width: 100% !important;
    overflow-x: auto !important;
    overflow-y: auto !important;
}

/* ══ Altair charts — RTL + overflow ════════════════════════════ */
.vega-embed { direction: ltr !important; max-width: 100% !important; overflow: hidden !important; }
[data-testid="stVegaLiteChart"] { max-width: 100% !important; overflow: hidden !important; }
.vega-embed canvas { max-width: 100% !important; }

/* ══ Expander ═══════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    background: var(--surface) !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Cairo', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: var(--t1) !important;
    padding: 12px 16px !important;
    background: var(--surface2) !important;
}
[data-testid="stExpander"] summary:hover {
    background: rgba(37,99,235,.06) !important;
    color: var(--blue) !important;
}

/* ══ Buttons ════════════════════════════════════════════════════ */
.stButton button {
    font-family: 'Cairo', sans-serif !important;
    font-size: 0.88rem !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all .15s !important;
}

/* ══ Metrics ════════════════════════════════════════════════════ */
[data-testid="stMetricLabel"] { font-family: 'Cairo', sans-serif !important; font-size: 0.78rem !important; }
[data-testid="stMetricValue"] { font-family: 'Cairo', sans-serif !important; }

/* ══ Captions / warnings / info ═════════════════════════════════ */
[data-testid="stCaptionContainer"], .stMarkdown small {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl !important;
}
.stAlert { font-family: 'Cairo', sans-serif !important; direction: rtl !important; border-radius: var(--r) !important; }

/* ══ Divider ════════════════════════════════════════════════════ */
hr { border-color: var(--border) !important; }

/* ══ Responsive — Tablet 768px ══════════════════════════════════ */
@media (max-width: 768px) {
    .block-container { padding: 1rem 1rem 2rem !important; }
    .ph { padding: 18px 20px; gap: 14px; }
    .ph-text h1 { font-size: 1.35rem !important; }
    .ph-text p  { font-size: 0.82rem !important; }
    .ph-badge   { display: none; }
    .kpi { padding: 14px 10px !important; gap: 10px; }
    .kpi-val { font-size: 1.5rem !important; }
    .sec { margin: 18px 0 12px; }
}

/* ══ Responsive — Mobile 480px ══════════════════════════════════ */
@media (max-width: 480px) {
    .block-container { padding: 0.75rem 0.75rem 1.5rem !important; }
    .ph { padding: 12px 14px; gap: 10px; }
    .ph-icon { font-size: 1.8rem; }
    .ph-text h1 { font-size: 1.1rem !important; }
    .ph-text p  { font-size: 0.74rem !important; }
    .kpi { padding: 10px 8px !important; gap: 8px; min-height: 60px; }
    .kpi-icon-box { width: 36px !important; height: 36px !important; font-size: 0.95rem !important; }
    .kpi-val { font-size: 1.3rem !important; }
    .kpi-lbl { font-size: 0.68rem !important; }
    .wc, .store-chip { padding: 10px 12px !important; }
    .pt { font-size: 1.2rem !important; }
    .ps { font-size: 0.8rem !important; }
    .sidebar-toggle { width: 38px !important; height: 38px !important; font-size: 1.2rem !important; }
    [data-testid="stSlider"] { padding: 2px !important; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_products():
    try:
        with open(BASE_DIR / "products_all.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        return df.dropna(subset=["price"])
    except Exception:
        return pd.DataFrame(columns=["name", "price", "store", "url", "timestamp", "currency"])


@st.cache_data(ttl=300)
def load_groups():
    try:
        with open(BASE_DIR / "matched_groups.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
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
    except Exception:
        return pd.DataFrame(columns=["name", "price", "store", "timestamp"])


@st.cache_data(ttl=300)
def load_work_descriptions():
    try:
        with open(BASE_DIR / "work_descriptions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def reload_all():
    load_products.clear()
    load_groups.clear()
    load_history.clear()
    load_work_descriptions.clear()


# ─────────────────────────────────────────────────────────────────
# ACTIONS (local only)
# ─────────────────────────────────────────────────────────────────
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
            st.error(f"❌ فشل: {str(e)[:120]}")


def run_ai_only():
    with st.spinner("عميل AI يعمل ..."):
        try:
            subprocess.run([sys.executable, str(BASE_DIR / "ai_agent.py")], timeout=600, check=True, capture_output=True)
            reload_all()
            st.success("✅ تم التوليد بنجاح")
            st.rerun()
        except Exception as e:
            st.error(f"❌ فشل: {str(e)[:120]}")


# ─────────────────────────────────────────────────────────────────
# SCHEDULER (local only)
# ─────────────────────────────────────────────────────────────────
if not IS_CLOUD and "scheduler_started" not in st.session_state:
    try:
        from scheduler import start_scheduler
        st.session_state["scheduler"] = start_scheduler()
        st.session_state["scheduler_started"] = True
    except Exception:
        st.session_state["scheduler_started"] = False

sched_ok = not IS_CLOUD and st.session_state.get("scheduler_started", False)

# ─────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────
df         = load_products()
groups     = load_groups()
history_df = load_history()
work_data  = load_work_descriptions()
api_key    = get_api_key()

n_products = len(df)
n_stores   = df["store"].nunique() if not df.empty else 0
n_groups   = len(groups)
n_ai       = len(work_data.get("work_items", []))
avg_saving = round(sum(g.get("savings_pct", 0) for g in groups) / len(groups), 1) if groups else 0


# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:18px 0 14px;text-align:center">
        <div style="font-size:1.9rem;margin-bottom:5px">⚡</div>
        <div style="font-size:1rem;font-weight:700;color:#0f172a">مقارنة الأسعار</div>
        <div style="font-size:0.73rem;color:#94a3b8;margin-top:2px">الكويت الكهربائية</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    page = st.radio(
        "nav",
        ["🏠 الرئيسية", "📦 المنتجات", "📂 الفئات والتفريعات",
         "⚖️ مقارنة الأسعار", "🏆 أفضل العروض",
         "🤖 توصيف الأعمال", "📈 تاريخ الأسعار", "📊 الرسوم البيانية"],
        label_visibility="collapsed",
    )

    st.divider()

    if IS_CLOUD:
        st.markdown("""
        <div class="cloud-info">
            <b>☁️ Streamlit Cloud</b><br>
            البيانات تُقرأ من ملفات JSON الجاهزة.
        </div>
        """, unsafe_allow_html=True)
        if st.button("♻️ مسح الكاش", use_container_width=True):
            reload_all(); st.rerun()
    else:
        with st.popover("⚙️ تحديث البيانات", use_container_width=True):
            st.markdown("**خيارات التحديث**")
            if st.button("🔄 تحديث البيانات فقط", use_container_width=True):
                run_update(run_ai=False)
            if st.button("🤖 تحديث + توصيف الأعمال", use_container_width=True):
                run_update(run_ai=True)
            if st.button("♻️ مسح الكاش", use_container_width=True):
                reload_all(); st.rerun()

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.metric("المنتجات", f"{n_products:,}")
        st.metric("التوصيف",  n_ai)
    with c2:
        st.metric("المتاجر",  n_stores)
        st.metric("المطابقة", n_groups)

    st.divider()
    if IS_CLOUD:
        st.caption("☁️ وضع القراءة — Streamlit Cloud")
    else:
        st.caption(f"🔄 الجدولة: {'✅ تعمل' if sched_ok else '⚠️ متوقفة'}")
    if not df.empty and "timestamp" in df.columns:
        st.caption(f"📅 آخر تحديث: {df['timestamp'].max()}")
    if not api_key:
        st.caption("⚠️ مفتاح API غير موجود")


# ─────────────────────────────────────────────────────────────────
# SIDEBAR TOGGLE BUTTON
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<script>
function toggleSidebar() {
    const sb = document.querySelector('section[data-testid="stSidebar"]');
    if (sb) sb.style.display = sb.style.display === 'none' ? 'block' : 'none';
}
</script>
<button class="sidebar-toggle" onclick="toggleSidebar()" title="القائمة الجانبية">☰</button>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────
def extract_category(name: str) -> str:
    kw = {
        "كيبل": "الكيبلات والأسلاك",  "سلك": "الكيبلات والأسلاك",
        "مفتاح": "المفاتيح والقواطع", "قاطع": "المفاتيح والقواطع",
        "مصابيح": "المصابيح والإضاءة","مصباح": "المصابيح والإضاءة",
        "led": "المصابيح والإضاءة",   "لمبة": "المصابيح والإضاءة",
        "مقبس": "المقابس والمنافذ",   "منفذ": "المقابس والمنافذ",
        "ترانس": "المحولات",           "محول": "المحولات",
        "بطارية": "البطاريات",         "مولد": "المولدات",
        "مروحة": "المراوح والتهوية",  "مراوح": "المراوح والتهوية",
        "مكيف": "تكييف الهواء",        "ثلاجة": "الأجهزة المنزلية",
        "غسالة": "الأجهزة المنزلية",  "سخان": "سخانات المياه",
        "شاحن": "أجهزة الشحن",
    }
    low = name.lower()
    for k, cat in kw.items():
        if k in low:
            return cat
    return "أخرى"


def clean_url(url) -> str | None:
    """Return url only if it starts with http, else None."""
    return url if (url and isinstance(url, str) and url.startswith("http")) else None


def make_chart_base(title: str = "") -> dict:
    """Common Altair chart config kwargs."""
    return dict(title=title)


# ─────────────────────────────────────────────────────────────────
# ══ الرئيسية ════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
if page == "🏠 الرئيسية":
    st.markdown("""
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
        st.warning("⚠️ لا توجد بيانات — " + ("يتم تحديثها تلقائياً" if IS_CLOUD else "استخدم ⚙️ تحديث البيانات"))

    kpis_data = [
        ("📦", "blue",   f"{n_products:,}", "المنتجات"),
        ("🏪", "teal",   n_stores,          "المتاجر"),
        ("⚖️", "blue",   n_groups,          "المطابقة"),
        ("💰", "amber",  f"{avg_saving}%",  "التوفير"),
        ("🤖", "violet", n_ai,              "التوصيف"),
    ]
    kpi_cols = st.columns(5)
    for idx, (icon, color, val, lbl) in enumerate(kpis_data):
        with kpi_cols[idx]:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-icon-box {color}">{icon}</div>
                <div class="kpi-body">
                    <div class="kpi-val">{val}</div>
                    <div class="kpi-lbl">{lbl}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    if not df.empty:
        st.markdown('<div class="sec"><span class="sec-icon">🏪</span><span class="sec-title">المتاجر</span></div>', unsafe_allow_html=True)
        sc = df.groupby("store").size().reset_index(name="n")
        cols = st.columns(min(4, len(sc)))
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
                <div class="wc-desc">{item.get('description','')[:80]}...</div>
                <div class="wc-meta">
                    <span>📊 <span class="p">{item.get('min_price','—')} KD</span></span>
                    <span class="s">🏪 {item.get('best_store','—')}</span>
                </div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ══ المنتجات ════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
elif page == "📦 المنتجات":
    st.markdown('<div class="pt">📦 قائمة المنتجات</div><div class="ps">تصفح وابحث في المنتجات الكهربائية</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات")
    else:
        # ── Filters inside a styled card ───────────────────────────
        with st.container():
            search = st.text_input("🔍 بحث باسم المنتج", placeholder="اكتب كلمة للبحث ...")
            fc1, fc2 = st.columns([1, 2])
            with fc1:
                stores = ["الكل"] + sorted(df["store"].unique().tolist())
                sel_store = st.selectbox("🏪 المتجر", stores)
            with fc2:
                mn, mx = float(df["price"].min()), float(df["price"].max())
                if mn < mx:
                    price_range = st.slider("💰 نطاق السعر (KD)", mn, mx, (mn, mx), step=0.1)
                else:
                    price_range = (mn, mx)
                    st.info(f"السعر الثابت: {mn} KD")

        filt = df.copy()
        if search:
            filt = filt[filt["name"].str.contains(search, case=False, na=False)]
        if sel_store != "الكل":
            filt = filt[filt["store"] == sel_store]
        filt = filt[(filt["price"] >= price_range[0]) & (filt["price"] <= price_range[1])]

        st.caption(f"**{len(filt):,}** منتج")

        show = filt[["name", "price", "store", "url"]].copy()
        show["url"] = show["url"].apply(clean_url)
        show.columns = ["المنتج", "السعر (KD)", "المتجر", "رابط"]
        st.dataframe(
            show,
            use_container_width=True,
            hide_index=True,
            height=min(400, max(200, len(show) * 35 + 40)),
            column_config={
                "المنتج":    st.column_config.TextColumn("المنتج",    width="large"),
                "السعر (KD)":st.column_config.NumberColumn("السعر",   width="small", format="%.2f KD"),
                "المتجر":   st.column_config.TextColumn("المتجر",    width="medium"),
                "رابط":     st.column_config.LinkColumn("رابط",      width="small",  display_text="🔗 فتح"),
            }
        )


# ─────────────────────────────────────────────────────────────────
# ══ الفئات والتفريعات ═══════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
elif page == "📂 الفئات والتفريعات":
    st.markdown('<div class="pt">📂 الفئات والتفريعات</div><div class="ps">تصنيف المنتجات حسب النوع</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات")
    else:
        df_cat = df.copy()
        df_cat["category"] = df_cat["name"].apply(extract_category)
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

        st.markdown('<div class="sec"><span class="sec-icon">📋</span><span class="sec-title">تفصيل المنتجات</span></div>', unsafe_allow_html=True)
        sel_cat = st.selectbox("اختر فئة", sorted(cat_counts.index.tolist()))
        cat_products = df_cat[df_cat["category"] == sel_cat]
        st.caption(f"**{len(cat_products)}** منتج في فئة: **{sel_cat}**")

        for store in sorted(cat_products["store"].unique()):
            store_data = cat_products[cat_products["store"] == store]
            with st.expander(f"🏪 {store[:30]} ({len(store_data)} منتج)"):
                show = store_data[["name", "price", "url"]].copy()
                show["url"] = show["url"].apply(clean_url)
                show.columns = ["المنتج", "السعر (KD)", "رابط"]
                st.dataframe(
                    show,
                    use_container_width=True,
                    hide_index=True,
                    height=min(350, max(120, len(show) * 35 + 40)),
                    column_config={
                        "المنتج":    st.column_config.TextColumn("المنتج",    width="large"),
                        "السعر (KD)":st.column_config.NumberColumn("السعر",   width="small", format="%.2f KD"),
                        "رابط":     st.column_config.LinkColumn("رابط",      width="small",  display_text="🔗 فتح"),
                    }
                )


# ─────────────────────────────────────────────────────────────────
# ══ مقارنة الأسعار ══════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
elif page == "⚖️ مقارنة الأسعار":
    st.markdown('<div class="pt">⚖️ مقارنة الأسعار</div><div class="ps">نفس المنتج من متاجر مختلفة</div>', unsafe_allow_html=True)

    if not groups:
        st.warning("لا توجد بيانات مطابقة")
    else:
        q = st.text_input("🔍 ابحث عن منتج", placeholder="اكتب اسم المنتج ...")
        filtered_groups = [g for g in groups if not q or q.lower() in g["canonical_name"].lower()]
        st.caption(f"**{len(filtered_groups)}** مجموعة مطابقة")

        for g in filtered_groups[:50]:
            short = g["canonical_name"][:40] + ("..." if len(g["canonical_name"]) > 40 else "")
            saving = g.get("savings_pct", 0)
            badge  = f" 💰 توفير {saving}%" if saving > 0 else ""
            with st.expander(f"📦 {short}  —  أفضل سعر: {g['best_price']} KD{badge}"):
                rows = []
                for p in g["products"]:
                    url_val = p.get("url", "") or ""
                    rows.append({
                        "✔":         "✅" if p["price"] == g["best_price"] else "  ",
                        "المتجر":    p["store"],
                        "السعر (KD)":p["price"],
                        "رابط":      url_val if url_val.startswith("http") else None,
                    })
                comp_df = pd.DataFrame(rows)
                st.dataframe(
                    comp_df,
                    use_container_width=True,
                    hide_index=True,
                    height=min(250, len(comp_df) * 35 + 40),
                    column_config={
                        "✔":         st.column_config.TextColumn("",         width="small"),
                        "المتجر":    st.column_config.TextColumn("المتجر",   width="medium"),
                        "السعر (KD)":st.column_config.NumberColumn("السعر",  width="small", format="%.2f KD"),
                        "رابط":     st.column_config.LinkColumn("رابط",     width="small",  display_text="🔗"),
                    }
                )


# ─────────────────────────────────────────────────────────────────
# ══ أفضل العروض ════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
elif page == "🏆 أفضل العروض":
    st.markdown('<div class="pt">🏆 أفضل العروض</div><div class="ps">أكبر فارق سعري بين المتاجر</div>', unsafe_allow_html=True)

    if not groups:
        st.warning("لا توجد بيانات")
    else:
        with st.container():
            min_save = st.slider("الحد الأدنى للتوفير (%)", 0, 100, 10, step=5)

        deals = [
            g for g in sorted(groups, key=lambda x: x.get("savings_pct", 0), reverse=True)
            if g.get("savings_pct", 0) >= min_save
        ]
        st.caption(f"**{len(deals)}** عرض بتوفير ≥ {min_save}%")

        if deals:
            dd = pd.DataFrame([{
                "المنتج":     g["canonical_name"][:48],
                "أفضل متجر": g.get("best_store", "—"),
                "أفضل سعر":  g["best_price"],
                "توفير %":    g["savings_pct"],
            } for g in deals[:100]])
            st.dataframe(
                dd,
                use_container_width=True,
                hide_index=True,
                height=min(420, max(200, len(dd) * 35 + 40)),
                column_config={
                    "المنتج":    st.column_config.TextColumn("المنتج",       width="large"),
                    "أفضل متجر":st.column_config.TextColumn("أفضل متجر",    width="medium"),
                    "أفضل سعر": st.column_config.NumberColumn("أفضل سعر",   width="small", format="%.2f KD"),
                    "توفير %":   st.column_config.NumberColumn("توفير %",    width="small", format="%.0f%%"),
                }
            )

            if len(deals) >= 3:
                st.markdown('<div class="sec"><span class="sec-icon">📊</span><span class="sec-title">أفضل 15 عرضاً بيانياً</span></div>', unsafe_allow_html=True)
                top_n = min(15, len(deals))
                cd = pd.DataFrame([{
                    "المنتج":   g["canonical_name"][:32],
                    "توفير %":  g["savings_pct"],
                } for g in deals[:top_n]])
                bar = (
                    alt.Chart(cd)
                    .mark_bar(
                        color="#2563eb",
                        cornerRadiusTopRight=5,
                        cornerRadiusBottomRight=5,
                    )
                    .encode(
                        x=alt.X("توفير %:Q",
                                title="نسبة التوفير %",
                                axis=alt.Axis(labelFont="Cairo", labelFontSize=11, titleFont="Cairo", titleFontSize=12)),
                        y=alt.Y("المنتج:N",
                                sort="-x",
                                axis=alt.Axis(labelFont="Cairo", labelFontSize=10,
                                              labelLimit=220, labelPadding=6)),
                        tooltip=[
                            alt.Tooltip("المنتج:N",  title="المنتج"),
                            alt.Tooltip("توفير %:Q", title="التوفير %", format=".0f"),
                        ],
                    )
                    .properties(height=max(280, top_n * 28), padding={"left": 10, "right": 20, "top": 10, "bottom": 10})
                    .configure_axis(labelFont="Cairo", labelFontSize=10, titleFont="Cairo")
                    .configure_view(stroke=None)
                )
                st.altair_chart(bar, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
# ══ توصيف الأعمال ════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
elif page == "🤖 توصيف الأعمال":
    st.markdown('<div class="pt">🤖 توصيف الأعمال</div><div class="ps">بنود أعمال الكهرباء بالذكاء الاصطناعي</div>', unsafe_allow_html=True)

    if not api_key:
        st.warning("⚠️ مفتاح Anthropic API غير موجود — أضفه في ملف `.env` أو Streamlit Secrets باسم `ANTHROPIC_API_KEY`")

    if not work_data or not work_data.get("work_items"):
        st.info("لم يتم التوليد بعد.")
        if not IS_CLOUD and api_key:
            if st.button("🚀 توليد الآن", type="primary"):
                run_ai_only()
        elif IS_CLOUD:
            st.info("☁️ التوليد يتم من السيرفر المحلي. البيانات تُقرأ تلقائياً عند رفعها.")
    else:
        wi   = work_data["work_items"]
        cats = work_data.get("categories_summary", {})

        k1, k2, k3 = st.columns(3)
        for col, icon, color, val, lbl in [
            (k1, "📋", "blue",   len(wi),  "البنود"),
            (k2, "📂", "teal",   len(cats),"الفئات"),
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
            sw = st.text_input("🔍 بحث في التوصيفات")
        with cf2:
            sc_sel = st.selectbox("📂 الفئة", ["الكل"] + sorted(cats.keys()))

        fi = wi
        if sw:
            fi = [i for i in fi if sw.lower() in i.get("description", "").lower()]
        if sc_sel != "الكل":
            fi = [i for i in fi if i.get("category") == sc_sel]

        st.caption(f"**{len(fi)}** بند")
        if fi:
            td = pd.DataFrame([{
                "رقم":   i.get("item_no", n + 1),
                "الوصف": i.get("description", "")[:60],
                "الفئة": i.get("category", "—"),
                "النطاق السعري": f"{i.get('min_price','—')} – {i.get('max_price','—')} KD",
            } for n, i in enumerate(fi)])
            st.dataframe(
                td,
                use_container_width=True,
                hide_index=True,
                height=min(450, max(200, len(td) * 35 + 40)),
                column_config={
                    "رقم":           st.column_config.NumberColumn("رقم",       width="small"),
                    "الوصف":         st.column_config.TextColumn("الوصف",       width="large"),
                    "الفئة":         st.column_config.TextColumn("الفئة",       width="medium"),
                    "النطاق السعري": st.column_config.TextColumn("النطاق السعري", width="medium"),
                }
            )


# ─────────────────────────────────────────────────────────────────
# ══ تاريخ الأسعار ════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
elif page == "📈 تاريخ الأسعار":
    st.markdown('<div class="pt">📈 تاريخ الأسعار</div><div class="ps">تتبع تغير السعر عبر الزمن</div>', unsafe_allow_html=True)

    if history_df.empty:
        st.info("لا توجد بيانات تاريخية بعد — ستظهر بعد أول تحديثَين.")
    else:
        sel = st.selectbox("اختر منتجاً", sorted(history_df["name"].unique().tolist()))
        if sel:
            ph = history_df[history_df["name"] == sel].sort_values("timestamp")
            line = (
                alt.Chart(ph)
                .mark_line(point=alt.OverlayMarkDef(filled=True, size=60), strokeWidth=2.5)
                .encode(
                    x=alt.X("timestamp:T",
                            title="التاريخ",
                            axis=alt.Axis(labelFont="Cairo", labelFontSize=10,
                                          titleFont="Cairo", format="%Y-%m-%d",
                                          labelAngle=-30, labelPadding=8)),
                    y=alt.Y("price:Q",
                            title="السعر (KD)",
                            axis=alt.Axis(labelFont="Cairo", labelFontSize=10,
                                          titleFont="Cairo")),
                    color=alt.Color("store:N",
                                    legend=alt.Legend(labelFont="Cairo", labelFontSize=11,
                                                       titleFont="Cairo", title="المتجر")),
                    tooltip=[
                        alt.Tooltip("store:N",     title="المتجر"),
                        alt.Tooltip("price:Q",     title="السعر", format=".2f"),
                        alt.Tooltip("timestamp:T", title="التاريخ", format="%Y-%m-%d"),
                    ],
                )
                .properties(height=380, padding={"left": 10, "right": 20, "top": 10, "bottom": 30})
                .configure_axis(labelFont="Cairo", labelFontSize=10, titleFont="Cairo")
                .configure_legend(labelFont="Cairo", labelFontSize=11)
                .configure_view(stroke=None)
            )
            st.altair_chart(line, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
# ══ الرسوم البيانية ══════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
elif page == "📊 الرسوم البيانية":
    st.markdown('<div class="pt">📊 الرسوم البيانية</div><div class="ps">تحليل بصري للأسعار والمتاجر</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات")
    else:
        r1c1, r1c2 = st.columns(2)

        # ── توزيع الأسعار (Histogram) ─────────────────────────────
        with r1c1:
            st.markdown('<div class="sec"><span class="sec-icon">📉</span><span class="sec-title">توزيع الأسعار</span></div>', unsafe_allow_html=True)
            hist = (
                alt.Chart(df)
                .mark_bar(color="#2563eb", opacity=0.85, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    alt.X("price:Q",
                          bin=alt.Bin(maxbins=30),
                          title="السعر (KD)",
                          axis=alt.Axis(labelFont="Cairo", labelFontSize=10,
                                        titleFont="Cairo", labelPadding=6)),
                    alt.Y("count()",
                          title="العدد",
                          axis=alt.Axis(labelFont="Cairo", labelFontSize=10,
                                        titleFont="Cairo")),
                    tooltip=[
                        alt.Tooltip("price:Q",   bin=True, title="النطاق"),
                        alt.Tooltip("count():Q",          title="العدد"),
                    ],
                )
                .properties(height=320, padding={"left": 10, "right": 10, "top": 10, "bottom": 20})
                .configure_axis(labelFont="Cairo", labelFontSize=10, titleFont="Cairo")
                .configure_view(stroke=None)
            )
            st.altair_chart(hist, use_container_width=True)

        # ── متوسط السعر حسب المتجر (Horizontal bar) ───────────────
        with r1c2:
            st.markdown('<div class="sec"><span class="sec-icon">🏪</span><span class="sec-title">متوسط السعر حسب المتجر</span></div>', unsafe_allow_html=True)
            avg_df = df.groupby("store", as_index=False)["price"].mean().round({"price": 2})
            ab = (
                alt.Chart(avg_df)
                .mark_bar(color="#0d9488", cornerRadiusTopRight=5, cornerRadiusBottomRight=5)
                .encode(
                    y=alt.Y("store:N",
                            sort="-x",
                            title="",
                            axis=alt.Axis(labelFont="Cairo", labelFontSize=11,
                                          labelLimit=180, labelPadding=8)),
                    x=alt.X("price:Q",
                            title="متوسط السعر (KD)",
                            axis=alt.Axis(labelFont="Cairo", labelFontSize=10,
                                          titleFont="Cairo")),
                    tooltip=[
                        alt.Tooltip("store:N",  title="المتجر"),
                        alt.Tooltip("price:Q",  title="متوسط السعر", format=".2f"),
                    ],
                )
                .properties(height=320, padding={"left": 10, "right": 20, "top": 10, "bottom": 20})
                .configure_axis(labelFont="Cairo", labelFontSize=10, titleFont="Cairo")
                .configure_view(stroke=None)
            )
            st.altair_chart(ab, use_container_width=True)
