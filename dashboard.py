import os
import streamlit as st
import pandas as pd
import altair as alt
import json
import subprocess
import sys
import numpy as np
from pathlib import Path
from analytics import (
    detect_anomalies,
    calculate_inflation,
    calculate_copper_correlation,
    get_cost_breakdown_chart_data,
    generate_court_report,
    export_report_as_json,
)

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
# CSS — Minimal Cream Theme (inspired by modern analytics UI)
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;900&display=swap');

/* ══ Design tokens ══════════════════════════════════════════════ */
:root {
    --bg:       #f5f2ec;
    --surface:  #ffffff;
    --surface2: #ede9e1;
    --surface3: #f0ece4;
    --border:   #e2ddd5;
    --border2:  #ccc8c0;
    --purple:   #8577ce;
    --purple-l: #b3a9e4;
    --purple-d: #6658b4;
    --coral:    #d97561;
    --coral-l:  #eda897;
    --sage:     #7a9e7e;
    --sage-l:   #a8c4aa;
    --amber:    #c9974a;
    --amber-l:  #e4bc8a;
    --t1:       #1a1a1a;
    --t2:       #6b6560;
    --t3:       #a09a94;
    --r:        14px;
    --r-lg:     20px;
    --r-pill:   50px;
    --sh:       0 4px 20px rgba(0,0,0,.07), 0 1px 4px rgba(0,0,0,.04);
    --sh-sm:    0 2px 10px rgba(0,0,0,.05), 0 1px 2px rgba(0,0,0,.03);
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
    border-left: 1px solid var(--border) !important;
    box-shadow: var(--sh-sm) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--t1) !important;
    font-family: 'Cairo', sans-serif !important;
}
section[data-testid="stSidebar"] hr { border-color: var(--border) !important; margin: 8px 0 !important; }
section[data-testid="stSidebar"] [data-testid="stMetricLabel"] * { color: var(--t3) !important; font-size: 0.7rem !important; }
section[data-testid="stSidebar"] [data-testid="stMetricValue"] * { color: var(--purple) !important; font-size: 1.2rem !important; font-weight: 700 !important; }
section[data-testid="stSidebar"] .stRadio label {
    border-radius: var(--r-pill) !important; padding: 9px 16px !important;
    cursor: pointer !important; transition: background .2s !important; color: var(--t2) !important;
    font-size: 0.88rem !important;
}
section[data-testid="stSidebar"] .stRadio label:hover { background: var(--surface2) !important; color: var(--t1) !important; }
section[data-testid="stSidebar"] .stRadio input:checked + label {
    background: var(--surface2) !important; color: var(--t1) !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] .stButton button {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    color: var(--t1) !important; border-radius: var(--r-pill) !important;
    font-family: 'Cairo', sans-serif !important; transition: all .2s !important;
    font-size: 0.86rem !important;
}
section[data-testid="stSidebar"] .stButton button:hover { background: var(--border) !important; }
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: var(--t3) !important; font-size: 0.72rem !important; }

/* ══ Hide collapse buttons ══════════════════════════════════════ */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
button[data-testid="stBaseButton-headerNoPadding"],
[role="button"][aria-label="Expand"],
button[aria-label="Expand"],
button[data-testid*="expanderButton"] { display: none !important; }

/* ══ Page header ════════════════════════════════════════════════ */
.ph {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: 28px 36px; margin-bottom: 24px;
    box-shadow: var(--sh);
    display: flex; align-items: center; gap: 20px;
}
.ph-icon { font-size: 2.2rem; line-height: 1; flex-shrink: 0; }
.ph-text { flex: 1; min-width: 0; }
.ph-text h1 { font-size: 1.55rem; font-weight: 700; color: var(--t1); margin: 0 0 4px; }
.ph-text p  { font-size: 0.86rem; color: var(--t2); margin: 0; }
.ph-badge {
    margin-right: auto; flex-shrink: 0;
    background: var(--surface2); color: var(--t2);
    border: 1px solid var(--border2); border-radius: var(--r-pill);
    padding: 6px 16px; font-size: 0.78rem; font-weight: 700;
}

/* ══ KPI cards ══════════════════════════════════════════════════ */
.kpi {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r-lg); padding: 22px 18px; box-shadow: var(--sh-sm);
    display: flex; align-items: center; gap: 16px;
    transition: all .25s; height: 100%; min-height: 90px;
}
.kpi:hover { box-shadow: var(--sh); transform: translateY(-2px); }
.kpi-icon-box {
    width: 50px; height: 50px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; flex-shrink: 0;
}
.kpi-icon-box.purple { background: rgba(133,119,206,.14); }
.kpi-icon-box.coral  { background: rgba(217,117, 97,.14); }
.kpi-icon-box.sage   { background: rgba(122,158,126,.14); }
.kpi-icon-box.amber  { background: rgba(201,151, 74,.14); }
.kpi-icon-box.blue   { background: rgba(133,119,206,.14); }
.kpi-icon-box.teal   { background: rgba(122,158,126,.14); }
.kpi-icon-box.violet { background: rgba(133,119,206,.14); }
.kpi-body { flex: 1; min-width: 0; }
.kpi-val  { font-size: 1.9rem; font-weight: 800; color: var(--t1); line-height: 1; letter-spacing: -0.03em; }
.kpi-lbl  { font-size: 0.76rem; color: var(--t3); margin-top: 5px; font-weight: 500; }

/* ══ Section header ═════════════════════════════════════════════ */
.sec {
    display: flex; align-items: center; gap: 10px;
    margin: 24px 0 14px; padding-bottom: 0;
    border-bottom: none;
}
.sec-icon  { font-size: 1rem; opacity: 0.7; }
.sec-title { font-size: 0.95rem; font-weight: 700; color: var(--t2); text-transform: uppercase; letter-spacing: 0.06em; }
.sec-badge {
    margin-right: auto; background: rgba(133,119,206,.12); color: var(--purple);
    border: 1px solid rgba(133,119,206,.25); border-radius: var(--r-pill);
    padding: 3px 12px; font-size: 0.72rem; font-weight: 700;
}

/* ══ Work card ══════════════════════════════════════════════════ */
.wc {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r); padding: 16px 18px;
    margin-bottom: 10px; box-shadow: var(--sh-sm); transition: all .2s;
}
.wc:hover { box-shadow: var(--sh); border-color: var(--border2); }
.wc-cat {
    display: inline-block; background: var(--surface2); color: var(--t2);
    border-radius: var(--r-pill); padding: 3px 12px;
    font-size: 0.72rem; font-weight: 700;
}
.wc-desc { font-weight: 600; font-size: 0.9rem; color: var(--t1); margin: 7px 0 5px; line-height: 1.5; }
.wc-meta { font-size: 0.82rem; color: var(--t2); display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.wc-meta .p { color: var(--sage); font-weight: 700; }
.wc-meta .s {
    background: var(--surface2); color: var(--t2);
    border-radius: var(--r-pill); padding: 2px 10px;
    font-size: 0.72rem; font-weight: 700;
}

/* ══ Page title ═════════════════════════════════════════════════ */
.pt { font-size: 1.4rem; font-weight: 800; color: var(--t1); margin-bottom: 2px; letter-spacing: -0.02em; }
.ps { font-size: 0.85rem; color: var(--t3); margin-bottom: 20px; font-weight: 400; }

/* ══ Store chip ═════════════════════════════════════════════════ */
.store-chip {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r-lg); padding: 18px 12px; box-shadow: var(--sh-sm);
    text-align: center; transition: all .2s;
}
.store-chip:hover { border-color: var(--border2); box-shadow: var(--sh); }
.store-chip .sc-num  { font-size: 1.7rem; font-weight: 800; color: var(--purple); letter-spacing: -0.03em; }
.store-chip .sc-name { font-weight: 600; font-size: 0.86rem; color: var(--t1); margin-top: 4px; }
.store-chip .sc-count{ font-size: 0.72rem; color: var(--t3); margin-top: 2px; }

/* ══ Cloud banner ═══════════════════════════════════════════════ */
.cloud-info {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: var(--r); padding: 12px 16px;
    font-size: 0.86rem; color: var(--t2); margin-bottom: 4px;
}
.cloud-info b { color: var(--t1); }

/* ══ Input controls ═════════════════════════════════════════════ */
.stTextInput input, .stSelectbox select {
    font-family: 'Cairo', sans-serif !important;
    font-size: 0.9rem !important;
    border-radius: var(--r) !important;
    border-color: var(--border) !important;
    background: var(--surface) !important;
    color: var(--t1) !important;
    direction: rtl !important;
}
.stTextInput label, .stSelectbox label, .stSlider label {
    font-family: 'Cairo', sans-serif !important;
    font-size: 0.86rem !important;
    color: var(--t2) !important;
    font-weight: 600 !important;
}
/* Slider */
.stSlider {
    width: 100% !important; max-width: 100% !important;
    overflow: visible !important; padding: 0 !important; margin: 0 !important;
}
[data-testid="stSlider"] {
    width: 100% !important; padding: 0 !important;
    margin: 0 !important; overflow: visible !important;
}
[data-testid="stSlider"] canvas { max-width: 100% !important; }
/* Selectbox */
[data-testid="stSelectbox"] { max-width: 100% !important; }
[data-testid="stSelectbox"] > div > div {
    font-family: 'Cairo', sans-serif !important;
    font-size: 0.88rem !important;
    background: var(--surface) !important;
    border-color: var(--border) !important;
    border-radius: var(--r) !important;
    color: var(--t1) !important;
}
/* Filter row */
.filter-row {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r); padding: 16px 18px;
    margin-bottom: 16px; box-shadow: var(--sh-sm);
}

/* ══ Dataframe / Table ══════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    overflow: hidden !important;
    box-shadow: var(--sh-sm) !important;
    background: var(--surface) !important;
    width: 100% !important; max-width: 100% !important; display: block !important;
}
[data-testid="stDataFrame"] > div {
    width: 100% !important; max-width: 100% !important;
    overflow-x: auto !important; overflow-y: auto !important;
}
[data-testid="stDataFrame"] canvas { max-width: 100% !important; }

/* ══ Altair charts ══════════════════════════════════════════════ */
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
    font-size: 0.9rem !important; font-weight: 600 !important;
    color: var(--t1) !important; padding: 12px 16px !important;
    background: var(--surface3) !important;
}
[data-testid="stExpander"] summary:hover { background: var(--surface2) !important; }

/* ══ Buttons ════════════════════════════════════════════════════ */
.stButton button {
    font-family: 'Cairo', sans-serif !important;
    font-size: 0.88rem !important;
    border-radius: var(--r-pill) !important;
    font-weight: 600 !important;
    transition: all .2s !important;
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--t1) !important;
}
.stButton button:hover {
    background: var(--border) !important;
    border-color: var(--border2) !important;
}
.stDownloadButton button {
    font-family: 'Cairo', sans-serif !important;
    border-radius: var(--r-pill) !important;
    font-weight: 600 !important;
    background: var(--t1) !important;
    color: var(--bg) !important;
    border: none !important;
}
.stDownloadButton button:hover {
    background: #333 !important;
    opacity: 0.9 !important;
}

/* ══ Metrics ════════════════════════════════════════════════════ */
[data-testid="stMetricLabel"] { font-family: 'Cairo', sans-serif !important; font-size: 0.78rem !important; color: var(--t3) !important; }
[data-testid="stMetricValue"] { font-family: 'Cairo', sans-serif !important; font-weight: 800 !important; letter-spacing: -0.03em !important; }
[data-testid="stMetricDelta"] { font-family: 'Cairo', sans-serif !important; }

/* ══ Captions / alerts ══════════════════════════════════════════ */
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
    .ph-text h1 { font-size: 1.25rem !important; }
    .ph-badge { display: none; }
    .kpi { padding: 16px 12px !important; gap: 12px; }
    .kpi-val { font-size: 1.6rem !important; }
    .kpi-icon-box { width: 42px !important; height: 42px !important; }
    .sec { margin: 18px 0 12px; }
}

/* ══ Responsive — Mobile 480px ══════════════════════════════════ */
@media (max-width: 480px) {
    .block-container { padding: 0.75rem 0.75rem 1.5rem !important; }
    .ph { padding: 14px 16px; gap: 10px; }
    .ph-icon { font-size: 1.7rem; }
    .ph-text h1 { font-size: 1.05rem !important; }
    .ph-text p  { font-size: 0.74rem !important; }
    .kpi { padding: 12px 10px !important; gap: 10px; min-height: 70px; }
    .kpi-icon-box { width: 38px !important; height: 38px !important; font-size: 1rem !important; }
    .kpi-val { font-size: 1.4rem !important; }
    .kpi-lbl { font-size: 0.68rem !important; }
    .wc, .store-chip { padding: 12px !important; }
    .pt { font-size: 1.2rem !important; }
    .ps { font-size: 0.78rem !important; }
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
         "🤖 توصيف الأعمال", "📈 تاريخ الأسعار", "📊 الرسوم البيانية",
         "🔍 كشف الشذوذ", "📊 ارتباط النحاس", "💰 تقسيم التكاليف",
         "📈 معدل التضخم", "⚖️ تقرير قانوني"],
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
        ("📦", "purple", f"{n_products:,}", "المنتجات"),
        ("🏪", "sage",   n_stores,          "المتاجر"),
        ("⚖️", "coral",  n_groups,          "المطابقة"),
        ("💰", "amber",  f"{avg_saving}%",  "التوفير"),
        ("🤖", "purple", n_ai,              "التوصيف"),
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
        # ── Filters ──────────────────────────────────────────────────
        search = st.text_input("🔍 بحث باسم المنتج", placeholder="اكتب كلمة للبحث ...")
        fc1, fc2 = st.columns([1, 1])
        with fc1:
            stores = ["الكل"] + sorted(df["store"].unique().tolist())
            sel_store = st.selectbox("🏪 المتجر", stores)
        with fc2:
            mn, mx = float(df["price"].min()), float(df["price"].max())
            if mn < mx:
                price_range = st.slider("💰 السعر (KD)", mn, mx, (mn, mx), step=0.1)
            else:
                price_range = (mn, mx)
                st.caption(f"السعر الثابت: {mn} KD")

        filt = df.copy()
        if search:
            filt = filt[filt["name"].str.contains(search, case=False, na=False)]
        if sel_store != "الكل":
            filt = filt[filt["store"] == sel_store]
        filt = filt[(filt["price"] >= price_range[0]) & (filt["price"] <= price_range[1])]

        st.caption(f"**{len(filt):,}** منتج")

        show = filt[["name", "price", "store", "url"]].copy()
        show["price"] = show["price"].apply(lambda x: f"{x:.2f}")
        show["url"] = show["url"].apply(clean_url)
        show.columns = ["المنتج", "السعر (KD)", "المتجر", "رابط"]
        st.dataframe(
            show,
            use_container_width=True,
            hide_index=True,
            height=min(420, max(150, len(show) * 32 + 50)),
            column_config={
                "المنتج":    st.column_config.TextColumn(width="large"),
                "السعر (KD)":st.column_config.TextColumn(width="small"),
                "المتجر":   st.column_config.TextColumn(width="medium"),
                "رابط":     st.column_config.LinkColumn(width="small", display_text="🔗"),
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
            with st.expander(f"🏪 {store[:30]} ({len(store_data)})"):
                show = store_data[["name", "price", "url"]].copy()
                show["price"] = show["price"].apply(lambda x: f"{x:.2f}")
                show["url"] = show["url"].apply(clean_url)
                show.columns = ["المنتج", "السعر (KD)", "رابط"]
                st.dataframe(
                    show,
                    use_container_width=True,
                    hide_index=True,
                    height=min(320, max(100, len(show) * 32 + 45)),
                    column_config={
                        "المنتج":    st.column_config.TextColumn(width="large"),
                        "السعر (KD)":st.column_config.TextColumn(width="small"),
                        "رابط":     st.column_config.LinkColumn(width="small", display_text="🔗"),
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
            short = g["canonical_name"][:36] + ("..." if len(g["canonical_name"]) > 36 else "")
            saving = g.get("savings_pct", 0)
            with st.expander(f"📦 {short} | أفضل: {g['best_price']} KD | توفير: {saving}%"):
                rows = []
                for p in g["products"]:
                    url_val = p.get("url", "") or ""
                    rows.append({
                        "✔":         "✅" if p["price"] == g["best_price"] else "",
                        "المتجر":    p["store"],
                        "السعر":     f"{p['price']:.2f}",
                        "رابط":      url_val if url_val.startswith("http") else None,
                    })
                comp_df = pd.DataFrame(rows)
                st.dataframe(
                    comp_df,
                    use_container_width=True,
                    hide_index=True,
                    height=min(220, max(100, len(comp_df) * 32 + 45)),
                    column_config={
                        "✔":     st.column_config.TextColumn(width="small"),
                        "المتجر":st.column_config.TextColumn(width="medium"),
                        "السعر":  st.column_config.TextColumn(width="small"),
                        "رابط":  st.column_config.LinkColumn(width="small", display_text="🔗"),
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
                "المنتج":     g["canonical_name"][:45],
                "المتجر":    g.get("best_store", "—"),
                "السعر":     f"{g['best_price']:.2f}",
                "توفير %":   f"{g['savings_pct']:.0f}%",
            } for g in deals[:100]])
            st.dataframe(
                dd,
                use_container_width=True,
                hide_index=True,
                height=min(450, max(150, len(dd) * 32 + 50)),
                column_config={
                    "المنتج":   st.column_config.TextColumn(width="large"),
                    "المتجر":  st.column_config.TextColumn(width="medium"),
                    "السعر":   st.column_config.TextColumn(width="small"),
                    "توفير %": st.column_config.TextColumn(width="small"),
                }
            )

            if len(deals) >= 3:
                st.markdown('<div class="sec"><span class="sec-icon">📊</span><span class="sec-title">أفضل 12 عرضاً</span></div>', unsafe_allow_html=True)
                top_n = min(12, len(deals))
                cd = pd.DataFrame([{
                    "المنتج":   g["canonical_name"][:35],
                    "التوفير":  g["savings_pct"],
                } for g in deals[:top_n]])
                bar = (
                    alt.Chart(cd)
                    .mark_bar(color="#8577ce", cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                    .encode(
                        x=alt.X("التوفير:Q",
                                title="نسبة التوفير %",
                                axis=alt.Axis(labelFont="Cairo", labelFontSize=10,
                                             titleFont="Cairo", titleFontSize=11, labelPadding=6)),
                        y=alt.Y("المنتج:N",
                                sort="-x",
                                axis=alt.Axis(labelFont="Cairo", labelFontSize=10,
                                             labelLimit=250, labelPadding=8)),
                        tooltip=[
                            alt.Tooltip("المنتج:N",  title="المنتج"),
                            alt.Tooltip("التوفير:Q", title="التوفير %", format=".0f"),
                        ],
                    )
                    .properties(height=max(280, top_n * 30),
                               padding={"left": 10, "right": 20, "top": 10, "bottom": 10})
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
                "#":    n + 1,
                "الوصف": i.get("description", "")[:58],
                "الفئة": i.get("category", "—"),
                "السعر": f"{i.get('min_price','—')} - {i.get('max_price','—')}",
            } for n, i in enumerate(fi)])
            st.dataframe(
                td,
                use_container_width=True,
                hide_index=True,
                height=min(480, max(150, len(td) * 32 + 50)),
                column_config={
                    "#":     st.column_config.TextColumn(width="small"),
                    "الوصف":  st.column_config.TextColumn(width="large"),
                    "الفئة":  st.column_config.TextColumn(width="medium"),
                    "السعر":  st.column_config.TextColumn(width="small"),
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
                            axis=alt.Axis(labelFont="Cairo", labelFontSize=9,
                                          titleFont="Cairo", format="%d/%m",
                                          labelAngle=-35, labelPadding=8)),
                    y=alt.Y("price:Q",
                            title="السعر (KD)",
                            axis=alt.Axis(labelFont="Cairo", labelFontSize=10,
                                          titleFont="Cairo", titlePadding=10)),
                    color=alt.Color("store:N",
                                    legend=alt.Legend(labelFont="Cairo", labelFontSize=10,
                                                       titleFont="Cairo", title="المتجر",
                                                       labelPadding=6)),
                    tooltip=[
                        alt.Tooltip("store:N",     title="المتجر"),
                        alt.Tooltip("price:Q",     title="السعر", format=".2f"),
                        alt.Tooltip("timestamp:T", title="التاريخ", format="%Y-%m-%d"),
                    ],
                )
                .properties(height=min(420, max(300, len(ph["store"].unique()) * 60)),
                           padding={"left": 10, "right": 30, "top": 10, "bottom": 40})
                .configure_axis(labelFont="Cairo", labelFontSize=10, titleFont="Cairo")
                .configure_legend(labelFont="Cairo", labelFontSize=10, titleFont="Cairo")
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
                .mark_bar(color="#8577ce", opacity=0.85, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    alt.X("price:Q",
                          bin=alt.Bin(maxbins=28),
                          title="السعر (KD)",
                          axis=alt.Axis(labelFont="Cairo", labelFontSize=9,
                                        titleFont="Cairo", labelPadding=6, labelAngle=-20)),
                    alt.Y("count()",
                          title="العدد",
                          axis=alt.Axis(labelFont="Cairo", labelFontSize=10,
                                        titleFont="Cairo", titlePadding=10)),
                    tooltip=[
                        alt.Tooltip("price:Q",   bin=True, title="النطاق"),
                        alt.Tooltip("count():Q",          title="العدد"),
                    ],
                )
                .properties(height=340, padding={"left": 10, "right": 20, "top": 10, "bottom": 30})
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
                .mark_bar(color="#7a9e7e", cornerRadiusTopRight=5, cornerRadiusBottomRight=5)
                .encode(
                    y=alt.Y("store:N",
                            sort="-x",
                            title="",
                            axis=alt.Axis(labelFont="Cairo", labelFontSize=10,
                                          labelLimit=220, labelPadding=12, labelAngle=0)),
                    x=alt.X("price:Q",
                            title="متوسط السعر (KD)",
                            axis=alt.Axis(labelFont="Cairo", labelFontSize=10,
                                          titleFont="Cairo", labelPadding=4)),
                    tooltip=[
                        alt.Tooltip("store:N",  title="المتجر"),
                        alt.Tooltip("price:Q",  title="متوسط السعر", format=".2f"),
                    ],
                )
                .properties(height=max(300, len(avg_df) * 35),
                           padding={"left": 10, "right": 20, "top": 10, "bottom": 20})
                .configure_axis(labelFont="Cairo", labelFontSize=10, titleFont="Cairo")
                .configure_view(stroke=None)
            )
            st.altair_chart(ab, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
# ══ كشف الشذوذ ══════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
elif page == "🔍 كشف الشذوذ":
    st.markdown('<div class="pt">🔍 كشف الشذوذ في الأسعار</div><div class="ps">تحديد الأسعار التي تختلف بشكل كبير عن متوسط السوق</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات")
    else:
        threshold = st.slider("عتبة الاختلاف (%)", min_value=5, max_value=50, value=20, step=5)
        anomalies = detect_anomalies(df, threshold_percent=threshold)

        if anomalies:
            st.success(f"✅ تم اكتشاف {len(anomalies)} حالات شاذة")

            anomaly_df = pd.DataFrame(anomalies)
            st.dataframe(
                anomaly_df[["المنتج", "المتجر", "السعر", "متوسط السوق", "الفرق %", "الحالة"]],
                use_container_width=True,
                hide_index=True,
                height=min(500, max(200, len(anomaly_df) * 35 + 50)),
                column_config={
                    "المنتج": st.column_config.TextColumn(width="medium"),
                    "المتجر": st.column_config.TextColumn(width="small"),
                    "السعر": st.column_config.TextColumn(width="small"),
                    "متوسط السوق": st.column_config.TextColumn(width="small"),
                    "الفرق %": st.column_config.TextColumn(width="small"),
                    "الحالة": st.column_config.TextColumn(width="medium"),
                }
            )

            st.markdown('<div class="sec"><span class="sec-icon">📊</span><span class="sec-title">الملخص الإحصائي</span></div>', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("إجمالي الحالات", len(anomalies))
            with col2:
                above = len([a for a in anomalies if "أعلى" in a["الحالة"]])
                st.metric("أعلى من السوق 🔴", above)
            with col3:
                below = len([a for a in anomalies if "أقل" in a["الحالة"]])
                st.metric("أقل من السوق 🟢", below)
            with col4:
                avg_diff = np.mean([float(a["الفرق %"].rstrip("%")) for a in anomalies])
                st.metric("متوسط الاختلاف", f"{avg_diff:.1f}%")
        else:
            st.info("✅ لا توجد أسعار شاذة في السوق الحالية")


# ─────────────────────────────────────────────────────────────────
# ══ ارتباط النحاس ══════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
elif page == "📊 ارتباط النحاس":
    st.markdown('<div class="pt">📊 ارتباط النحاس اللندني</div><div class="ps">تحليل الارتباط بين أسعار الكيبلات والنحاس العالمي</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات")
    else:
        corr_result = calculate_copper_correlation(df)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("معامل الارتباط", f"{corr_result['correlation']:.3f}")
        with col2:
            st.metric("حالة الارتباط", corr_result.get("interpretation", "—"))
        with col3:
            st.metric("سعر النحاس الحالي", corr_result.get("current_copper_price", "—"))

        st.info(f"💡 متوسط سعر الكيبلات: {corr_result.get('cable_avg_price', '—')}")

        # جدول توضيحي
        st.markdown('<div class="sec"><span class="sec-icon">📈</span><span class="sec-title">جودة الارتباط</span></div>', unsafe_allow_html=True)

        interp_map = {
            "ارتباط قوي ✅": {"أيقونة": "🔴", "الوصف": "ارتباط مباشر قوي: أسعار الكيبلات تتابع النحاس بقرب شديد"},
            "ارتباط متوسط ⚠️": {"أيقونة": "🟡", "الوصف": "ارتباط معتدل: هناك عوامل أخرى تؤثر على السعر"},
            "ارتباط ضعيف ❌": {"أيقونة": "🟢", "الوصف": "ارتباط ضعيف: عوامل السوق تسيطر أكثر من النحاس"},
        }

        for interp_text, details in interp_map.items():
            st.markdown(f"""
            <div style="padding:14px 16px;border-radius:14px;border-right:4px solid #8577ce;background:#f0ece4;margin:8px 0">
                <b style="color:#1a1a1a">{interp_text}</b><br>
                <span style="color:#6b6560;font-size:0.9rem">{details['الوصف']}</span>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ══ تقسيم التكاليف ═════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
elif page == "💰 تقسيم التكاليف":
    st.markdown('<div class="pt">💰 تقسيم التكاليف</div><div class="ps">توزيع المواد والعمالة والمصاريف العامة</div>', unsafe_allow_html=True)

    # Get category list
    breakdown_data = get_cost_breakdown_chart_data()
    categories = ["عام (Global)"]

    try:
        from cost_breakdown import get_cost_breakdown_chart_data as get_breakdown
        if callable(get_breakdown):
            try:
                full_data = get_breakdown()
                if isinstance(full_data, dict) and "breakdown_by_product_category" in str(full_data):
                    # Extract categories from the json file
                    import json
                    with open(BASE_DIR / "cost_breakdown.json", "r", encoding="utf-8") as f:
                        cost_data = json.load(f)
                        categories.extend(list(cost_data.get("breakdown_by_product_category", {}).keys()))
            except:
                pass
    except:
        # Fallback to reading JSON directly
        try:
            import json
            with open(BASE_DIR / "cost_breakdown.json", "r", encoding="utf-8") as f:
                cost_data = json.load(f)
                categories.extend(list(cost_data.get("breakdown_by_product_category", {}).keys()))
        except:
            categories = ["عام (Global)"]

    selected_category = st.selectbox("اختر الفئة", categories)

    if selected_category == "عام (Global)":
        data = get_cost_breakdown_chart_data()
    else:
        data = get_cost_breakdown_chart_data(category=selected_category)

    col1, col2, col3 = st.columns(3)

    # Extract percentages
    if isinstance(data, dict):
        materials = data.get("materials", data.get("المواد والخامات (Materials)", 45))
        labor = data.get("labor", data.get("العمالة (Labor)", 35))
        overhead = data.get("overhead", data.get("المصاريف العامة (Overhead)", 20))
    else:
        materials, labor, overhead = 45, 35, 20

    with col1:
        st.metric("🏭 المواد والخامات", f"{materials}%")
    with col2:
        st.metric("👷 العمالة", f"{labor}%")
    with col3:
        st.metric("📋 المصاريف العامة", f"{overhead}%")

    # Pie chart
    pie_data = pd.DataFrame({
        "النوع": ["المواد والخامات", "العمالة", "المصاريف العامة"],
        "النسبة": [materials, labor, overhead]
    })

    pie_chart = (
        alt.Chart(pie_data)
        .mark_arc(cornerRadius=5, innerRadius=50)
        .encode(
            theta="النسبة:Q",
            color=alt.Color("النوع:N",
                          scale=alt.Scale(domain=["المواد والخامات", "العمالة", "المصاريف العامة"],
                                        range=["#8577ce", "#7a9e7e", "#c9974a"]),
                          legend=alt.Legend(labelFont="Cairo")),
            tooltip=["النوع:N", "النسبة:Q"]
        )
        .properties(height=350, width=350)
        .configure_arc(stroke=None)
        .configure_legend(labelFont="Cairo", labelFontSize=11, titleFont="Cairo")
    )

    st.altair_chart(pie_chart, use_container_width=False)

    st.markdown('<div class="sec"><span class="sec-icon">📝</span><span class="sec-title">الشرح</span></div>', unsafe_allow_html=True)
    st.markdown(f"""
    - **المواد والخامات ({materials}%)**: تكلفة الأسلاك والكيبلات والمكونات الكهربائية
    - **العمالة ({labor}%)**: أجور الفنيين والعمال المتخصصين
    - **المصاريف العامة ({overhead}%)**: تكاليف إدارية وتشغيلية (إيجار، كهرباء، معدات)
    """)


# ─────────────────────────────────────────────────────────────────
# ══ معدل التضخم ═════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
elif page == "📈 معدل التضخم":
    st.markdown('<div class="pt">📈 معدل التضخم</div><div class="ps">تتبع التغيرات في الأسعار عبر الزمن</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات")
    else:
        inflation_data = calculate_inflation(df, days_back=30)

        if inflation_data:
            st.success(f"✅ تم حساب معدل التضخم لـ {len(inflation_data)} متاجر")

            inflation_rows = []
            for store, stats in inflation_data.items():
                inflation_rows.append({
                    "المتجر": store,
                    "السعر القديم": stats.get("السعر القديم", "—"),
                    "السعر الحالي": stats.get("السعر الحالي", "—"),
                    "معدل التضخم": stats.get("معدل التضخم", "—"),
                    "الاتجاه": stats.get("الاتجاه", "—")
                })

            inflation_df = pd.DataFrame(inflation_rows)
            st.dataframe(
                inflation_df,
                use_container_width=True,
                hide_index=True,
                height=min(400, max(150, len(inflation_df) * 35 + 50)),
                column_config={
                    "المتجر": st.column_config.TextColumn(width="medium"),
                    "السعر القديم": st.column_config.TextColumn(width="small"),
                    "السعر الحالي": st.column_config.TextColumn(width="small"),
                    "معدل التضخم": st.column_config.TextColumn(width="small"),
                    "الاتجاه": st.column_config.TextColumn(width="small"),
                }
            )

            # Summary statistics
            st.markdown('<div class="sec"><span class="sec-icon">📊</span><span class="sec-title">الملخص الإحصائي</span></div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            # Extract inflation percentages
            inflation_values = []
            for store, stats in inflation_data.items():
                try:
                    val = float(stats.get("معدل التضخم", "0").rstrip("%"))
                    inflation_values.append(val)
                except:
                    pass

            with col1:
                avg_inflation = np.mean(inflation_values) if inflation_values else 0
                st.metric("متوسط التضخم", f"{avg_inflation:+.1f}%")

            with col2:
                max_inflation = max(inflation_values) if inflation_values else 0
                st.metric("أعلى تضخم", f"{max_inflation:+.1f}%")

            with col3:
                min_inflation = min(inflation_values) if inflation_values else 0
                st.metric("أقل تضخم", f"{min_inflation:+.1f}%")
        else:
            st.info("لا توجد بيانات كافية لحساب معدل التضخم")


# ─────────────────────────────────────────────────────────────────
# ══ تقرير قانوني ═══════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────
elif page == "⚖️ تقرير قانوني":
    st.markdown('<div class="pt">⚖️ تقرير قانوني احترافي</div><div class="ps">تقرير معتمد لأغراض قانونية وقضائية</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات")
    else:
        # Generate report
        anomalies = detect_anomalies(df, threshold_percent=20)
        inflation_data = calculate_inflation(df, days_back=30)
        report = generate_court_report(df, groups, anomalies, inflation_data)

        # Display report header
        st.markdown(f"""
        <div style="padding:24px;background:#f0ece4;border-radius:16px;border-right:6px solid #8577ce;margin-bottom:20px">
            <div style="font-size:1.25rem;font-weight:800;color:#1a1a1a;margin-bottom:8px;letter-spacing:-0.02em">
                {report['report_title']}
            </div>
            <div style="color:#6b6560;font-size:0.92rem">
                <b>التاريخ:</b> {report['summary']['date_generated']} |
                <b>الوقت:</b> {report['summary']['time_generated']}<br>
                <b>الطابع:</b> {report['certification']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Summary statistics
        st.markdown('<div class="sec"><span class="sec-icon">📊</span><span class="sec-title">ملخص التقرير</span></div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("إجمالي المنتجات", report['summary']['total_products'])
        with col2:
            st.metric("عدد المتاجر", report['summary']['total_stores'])
        with col3:
            st.metric("الحالات الشاذة", report['summary']['total_anomalies'])
        with col4:
            st.metric("تقارير التضخم", len(inflation_data))

        # Findings
        st.markdown('<div class="sec"><span class="sec-icon">🔍</span><span class="sec-title">النتائج</span></div>', unsafe_allow_html=True)

        findings = report['findings']
        col1, col2, col3 = st.columns(3)
        with col1:
            status = "✅ نعم" if findings['anomalies_detected'] else "❌ لا"
            st.metric("الشذوذ المكتشف", status)
        with col2:
            st.metric("عدد الحالات", findings['anomaly_count'])
        with col3:
            status = "✅ نعم" if findings['inflation_trends'] else "❌ لا"
            st.metric("اتجاهات التضخم", status)

        # Legal statement
        st.markdown(f"""
        <div style="padding:16px;background:#ede9e1;border-radius:14px;border-right:4px solid #c9974a;margin:16px 0">
            <b>📋 البيان القانوني:</b><br>
            <span style="color:#6b6560;font-size:0.92rem">{report['legal_statement']}</span>
        </div>
        """, unsafe_allow_html=True)

        # Export button
        st.markdown('<div class="sec"><span class="sec-icon">💾</span><span class="sec-title">تصدير التقرير</span></div>', unsafe_allow_html=True)

        # Prepare export data
        export_data = {
            "report": report,
            "anomalies": anomalies,
            "inflation_data": inflation_data,
        }

        col1, col2 = st.columns(2)
        with col1:
            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 تحميل JSON",
                data=json_str,
                file_name=f"court_report_{report['timestamp'].replace(':','-')}.json",
                mime="application/json",
                use_container_width=True
            )

        with col2:
            if st.button("📄 معاينة JSON", use_container_width=True):
                with st.expander("محتوى الملف"):
                    st.json(export_data)
