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
# CLOUD DETECTION — disable scraper buttons on Streamlit Cloud
# ─────────────────────────────────────────────────────────────────
IS_CLOUD = (
    os.environ.get("STREAMLIT_SHARING_MODE") == "1"
    or os.environ.get("IS_STREAMLIT_CLOUD") == "1"
    or "STREAMLIT_SERVER_HEADLESS" in os.environ
    or os.path.exists("/mount/src")           # Streamlit Cloud mount path
)

# ─────────────────────────────────────────────────────────────────
# ANTHROPIC API KEY — read from env or st.secrets, never crash
# ─────────────────────────────────────────────────────────────────
def get_api_key() -> str | None:
    # 1) .env file (local development)
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=BASE_DIR / ".env")
    except ImportError:
        pass
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    # 2) Streamlit Cloud secrets
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
# DESIGN SYSTEM — Light Theme
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;900&display=swap');

/* ── Sidebar toggle ── */
.sidebar-toggle {
    position: fixed;
    top: 16px;
    right: 16px;
    z-index: 9999;
    background: var(--blue) !important;
    border: none !important;
    color: white !important;
    width: 44px !important;
    height: 44px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.4rem !important;
    box-shadow: var(--sh-md) !important;
    transition: all .2s !important;
    padding: 0 !important;
    line-height: 1 !important;
}
.sidebar-toggle:hover  { background: var(--blue-d) !important; }
.sidebar-toggle:active { transform: scale(0.95); }

/* ── Design tokens ── */
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
    --violet-l: #c4b5fd;
    --amber:    #f59e0b;
    --amber-d:  #b45309;
    --green:    #16a34a;
    --red:      #dc2626;
    --t1:       #0f172a;
    --t2:       #475569;
    --t3:       #94a3b8;
    --r:        10px;
    --r-lg:     16px;
    --sh:       0 4px 16px rgba(15,23,42,.10), 0 1px 4px rgba(15,23,42,.06);
    --sh-md:    0 2px 8px  rgba(15,23,42,.08), 0 1px 2px rgba(15,23,42,.04);
}

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
    background: var(--bg) !important;
    color: var(--t1) !important;
}

.block-container {
    padding: 1.5rem 2rem 2rem !important;
    max-width: 1400px;
    background: var(--bg) !important;
}

/* ══════════════════════════
   SIDEBAR
══════════════════════════ */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-left: 2px solid var(--blue) !important;
    box-shadow: var(--sh-md) !important;
}

section[data-testid="stSidebar"] * {
    color: var(--t1) !important;
    font-family: 'Cairo', sans-serif !important;
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
    color: var(--blue) !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] .stRadio label {
    border-radius: 8px !important;
    padding: 10px 14px !important;
    cursor: pointer !important;
    transition: background .15s !important;
    color: var(--t2) !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(37,99,235,.08) !important;
    color: var(--blue) !important;
}
section[data-testid="stSidebar"] .stRadio input:checked + label {
    background: rgba(37,99,235,.12) !important;
    color: var(--blue) !important;
    font-weight: 600 !important;
    border-right: 3px solid var(--blue) !important;
}

section[data-testid="stSidebar"] .stButton button {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--t1) !important;
    border-radius: 8px !important;
    font-family: 'Cairo', sans-serif !important;
    transition: all .15s !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: var(--border) !important;
    color: var(--blue) !important;
}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: var(--t3) !important;
    font-size: 0.72rem !important;
}

/* ══════════════════════════
   HIDE COLLAPSE / EXPAND
══════════════════════════ */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
button[data-testid="stBaseButton-headerNoPadding"],
[role="button"][aria-label="Expand"],
button[aria-label="Expand"],
button[data-testid*="expanderButton"] {
    display: none !important;
}

/* ══════════════════════════
   PAGE HEADER
══════════════════════════ */
.ph {
    background: linear-gradient(135deg, var(--surface2) 0%, rgba(37,99,235,.06) 100%);
    border: 1px solid rgba(37,99,235,.18);
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
    background: radial-gradient(circle at top right, rgba(37,99,235,.07), transparent);
    pointer-events: none;
}
.ph-icon {
    font-size: 2.8rem;
    line-height: 1;
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}
.ph-text          { flex: 1; position: relative; z-index: 1; }
.ph-text h1       { font-size: 1.8rem; font-weight: 700; color: var(--t1); margin: 0 0 6px; letter-spacing: -.02em; }
.ph-text p        { font-size: 0.92rem; color: var(--t2); margin: 0; }
.ph-badge {
    margin-right: auto;
    background: rgba(13,148,136,.12);
    color: var(--teal);
    border: 1px solid rgba(13,148,136,.25);
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
    background: var(--surface);
    border: 1px solid var(--border);
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
    border-color: rgba(37,99,235,.35);
    transform: translateY(-1px);
}
.kpi-icon-box {
    width: 48px; height: 48px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; flex-shrink: 0;
}
.kpi-icon-box.blue   { background: rgba(37,99,235,.12);  }
.kpi-icon-box.teal   { background: rgba(13,148,136,.12); }
.kpi-icon-box.violet { background: rgba(124,58,237,.12); }
.kpi-icon-box.amber  { background: rgba(245,158,11,.12); }
.kpi-body            { flex: 1; }
.kpi-val  { font-size: 1.8rem; font-weight: 700; color: var(--t1); line-height: 1; }
.kpi-lbl  { font-size: 0.8rem; color: var(--t3); margin-top: 4px; }

/* ══════════════════════════
   SECTION HEADER
══════════════════════════ */
.sec {
    display: flex; align-items: center; gap: 10px;
    margin: 28px 0 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid rgba(37,99,235,.12);
}
.sec-icon  { font-size: 1.2rem; }
.sec-title { font-size: 1.1rem; font-weight: 700; color: var(--t1); }
.sec-badge {
    margin-right: auto;
    background: rgba(124,58,237,.10);
    color: var(--violet);
    border: 1px solid rgba(124,58,237,.2);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.76rem; font-weight: 700;
}

/* ══════════════════════════
   WORK CARD
══════════════════════════ */
.wc {
    background: var(--surface);
    border: 1px solid rgba(124,58,237,.15);
    border-right: 3px solid var(--violet);
    border-radius: var(--r);
    padding: 16px 18px;
    margin-bottom: 10px;
    box-shadow: var(--sh-md);
    transition: all .2s;
}
.wc:hover { box-shadow: var(--sh); border-color: rgba(124,58,237,.3); }
.wc-cat {
    display: inline-block;
    background: rgba(124,58,237,.10);
    color: var(--violet);
    border-radius: 20px;
    padding: 3px 11px;
    font-size: 0.75rem; font-weight: 700;
}
.wc-desc { font-weight: 600; font-size: 0.94rem; color: var(--t1); margin: 8px 0 5px; line-height: 1.5; }
.wc-meta { font-size: 0.85rem; color: var(--t2); display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.wc-meta .p { color: var(--teal); font-weight: 700; }
.wc-meta .s {
    background: rgba(37,99,235,.10);
    color: var(--blue);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem; font-weight: 700;
}

/* ══════════════════════════
   PAGE TITLE
══════════════════════════ */
.pt { font-size: 1.5rem; font-weight: 700; color: var(--t1); margin-bottom: 3px; }
.ps { font-size: 0.88rem; color: var(--t2); margin-bottom: 22px; }

/* ══════════════════════════
   STORE GRID
══════════════════════════ */
.store-chip {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 16px 12px;
    box-shadow: var(--sh-md);
    text-align: center;
    transition: all .2s;
}
.store-chip:hover { border-color: var(--blue); box-shadow: var(--sh); }
.store-chip .sc-num  { font-size: 1.6rem; font-weight: 700; color: var(--blue); }
.store-chip .sc-name { font-weight: 700; font-size: 0.92rem; color: var(--t1); margin-top: 4px; }
.store-chip .sc-count{ font-size: 0.78rem; color: var(--t3); margin-top: 2px; }

/* ══════════════════════════
   CLOUD INFO BANNER
══════════════════════════ */
.cloud-info {
    background: rgba(37,99,235,.06);
    border: 1px solid rgba(37,99,235,.2);
    border-right: 4px solid var(--blue);
    border-radius: var(--r);
    padding: 14px 18px;
    font-size: 0.9rem;
    color: var(--t2);
    margin-bottom: 4px;
}
.cloud-info b { color: var(--blue); }

/* ══════════════════════════
   DATAFRAME
══════════════════════════ */
[data-testid="stDataFrame"] th {
    background: rgba(37,99,235,.07) !important;
    color: var(--blue) !important;
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
    background: rgba(37,99,235,.04) !important;
}

/* ══════════════════════════
   ALTAIR RTL
══════════════════════════ */
.vega-embed                      { direction: rtl !important; }
.vega-embed svg text             { direction: rtl !important; }
[data-testid="stVegaLiteChart"]  { direction: rtl !important; }

/* ══════════════════════════
   RESPONSIVE — Tablet
══════════════════════════ */
@media (max-width: 768px) {
    .block-container { padding: 1rem !important; }
    .ph { padding: 20px 24px; gap: 16px; }
    .ph h1 { font-size: 1.4rem !important; }
    .kpi { font-size: 0.9rem; }
}

/* ══════════════════════════
   RESPONSIVE — Mobile
══════════════════════════ */
@media (max-width: 480px) {
    .block-container { padding: 0.8rem 1rem !important; }
    .ph { padding: 14px; gap: 10px; }
    .ph-icon { font-size: 2rem; }
    .ph h1 { font-size: 1.1rem !important; }
    .ph p  { font-size: 0.75rem !important; }
    .kpi { padding: 12px 8px !important; gap: 8px; }
    .kpi-icon-box { width: 38px !important; height: 38px !important; font-size: 1rem !important; }
    .kpi-val { font-size: 1.4rem !important; }
    .kpi-lbl { font-size: 0.7rem !important; }
    .wc, .store-chip { padding: 10px 12px !important; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# DATA LOADERS — read JSON only, never run Playwright
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
# LOCAL-ONLY UPDATE ACTIONS (hidden on cloud)
# ─────────────────────────────────────────────────────────────────
def run_update(run_ai: bool = False):
    steps = [BASE_DIR / "scraper.py", BASE_DIR / "matcher.py"]
    if run_ai:
        steps.append(BASE_DIR / "ai_agent.py")
    with st.spinner("جاري التحديث ..."):
        try:
            for script in steps:
                subprocess.run(
                    [sys.executable, str(script)],
                    timeout=600, check=True, capture_output=True,
                )
            reload_all()
            st.success("✅ تم التحديث بنجاح")
            st.rerun()
        except Exception as e:
            st.error(f"❌ فشل: {str(e)[:120]}")


def run_ai_only():
    with st.spinner("عميل AI يعمل ..."):
        try:
            subprocess.run(
                [sys.executable, str(BASE_DIR / "ai_agent.py")],
                timeout=600, check=True, capture_output=True,
            )
            reload_all()
            st.success("✅ تم التوليد بنجاح")
            st.rerun()
        except Exception as e:
            st.error(f"❌ فشل: {str(e)[:120]}")


# ─────────────────────────────────────────────────────────────────
# SCHEDULER — local only
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
    <div style="padding:20px 0 16px;text-align:center">
        <div style="font-size:2rem;margin-bottom:6px">⚡</div>
        <div style="font-size:1.05rem;font-weight:700;color:#0f172a">مقارنة الأسعار</div>
        <div style="font-size:0.76rem;color:#94a3b8;margin-top:2px">الكويت الكهربائية</div>
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

    # ── Update section — hidden on cloud ──────────────────────────
    if IS_CLOUD:
        st.markdown("""
        <div class="cloud-info">
            <b>☁️ Streamlit Cloud</b><br>
            التحديث يتم من السيرفر تلقائياً. البيانات تُقرأ من ملفات JSON الجاهزة.
        </div>
        """, unsafe_allow_html=True)
        if st.button("♻️ مسح الكاش", use_container_width=True):
            reload_all()
            st.rerun()
    else:
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
        st.metric("التوصيف",  n_ai)
    with c2:
        st.metric("المتاجر",  n_stores)
        st.metric("المطابقة", n_groups)

    st.divider()
    if IS_CLOUD:
        st.caption("☁️ وضع القراءة — Streamlit Cloud")
    else:
        st.caption(f"🔄 الجدول: {'✅ يعمل' if sched_ok else '⚠️ متوقف'}")

    if not df.empty and "timestamp" in df.columns:
        st.caption(f"📅 آخر تحديث: {df['timestamp'].max()}")

    # API key status
    if not api_key:
        st.caption("⚠️ مفتاح API غير موجود")


# ─────────────────────────────────────────────────────────────────
# PAGES
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

# ── Helper: extract product category ─────────────────────────────
def extract_category(name: str) -> str:
    kw = {
        "كيبل": "الكيبلات والأسلاك",
        "سلك":  "الكيبلات والأسلاك",
        "مفتاح": "المفاتيح والقواطع",
        "قاطع":  "المفاتيح والقواطع",
        "مصابيح": "المصابيح والإضاءة",
        "مصباح":  "المصابيح والإضاءة",
        "led":    "المصابيح والإضاءة",
        "لمبة":   "المصابيح والإضاءة",
        "مقبس":  "المقابس والمنافذ",
        "منفذ":  "المقابس والمنافذ",
        "ترانس": "المحولات",
        "محول":  "المحولات",
        "بطارية": "البطاريات",
        "مولد":  "المولدات",
        "مروحة": "المراوح والتهوية",
        "مراوح": "المراوح والتهوية",
        "مكيف":  "تكييف الهواء",
        "ثلاجة": "الأجهزة المنزلية",
        "غسالة": "الأجهزة المنزلية",
        "سخان":  "سخانات المياه",
        "شاحن":  "أجهزة الشحن",
    }
    low = name.lower()
    for k, cat in kw.items():
        if k in low:
            return cat
    return "أخرى"


# ══════════════════════════════════════════════════════════════════
# 🏠 الرئيسية
# ══════════════════════════════════════════════════════════════════
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

    # KPI
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

    # Stores
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

    # AI preview
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


# ══════════════════════════════════════════════════════════════════
# 📦 المنتجات
# ══════════════════════════════════════════════════════════════════
elif page == "📦 المنتجات":
    st.markdown('<div class="pt">📦 قائمة المنتجات</div><div class="ps">تصفح وابحث في المنتجات الكهربائية</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات")
    else:
        search = st.text_input("🔍 بحث", placeholder="اكتب اسم المنتج...")
        c1, c2 = st.columns(2)
        with c1:
            stores = ["الكل"] + sorted(df["store"].unique().tolist())
            sel_store = st.selectbox("🏪 المتجر", stores)
        with c2:
            min_p, max_p = float(df["price"].min()), float(df["price"].max())
            price_range = st.slider("💰 السعر (KD)", min_p, max_p, (min_p, max_p))

        filt = df.copy()
        if search:
            filt = filt[filt["name"].str.contains(search, case=False, na=False)]
        if sel_store != "الكل":
            filt = filt[filt["store"] == sel_store]
        filt = filt[(filt["price"] >= price_range[0]) & (filt["price"] <= price_range[1])]

        st.caption(f"**{len(filt):,}** منتج")
        show = filt[["name", "price", "store"]].copy()
        show.columns = ["المنتج", "السعر (KD)", "المتجر"]
        st.dataframe(show, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════
# 📂 الفئات والتفريعات
# ══════════════════════════════════════════════════════════════════
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

        st.markdown("---")
        st.markdown('<div class="sec"><span class="sec-icon">📋</span><span class="sec-title">تفصيل المنتجات</span></div>', unsafe_allow_html=True)
        sel_cat = st.selectbox("اختر فئة", sorted(cat_counts.index.tolist()))
        cat_products = df_cat[df_cat["category"] == sel_cat]
        st.caption(f"**{len(cat_products)}** منتج في فئة: **{sel_cat}**")

        for store in sorted(cat_products["store"].unique()):
            store_data = cat_products[cat_products["store"] == store]
            with st.expander(f"🏪 {store[:25]} ({len(store_data)})"):
                show = store_data[["name", "price"]].copy()
                show.columns = ["المنتج", "السعر (KD)"]
                st.dataframe(show, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════
# ⚖️ مقارنة الأسعار
# ══════════════════════════════════════════════════════════════════
elif page == "⚖️ مقارنة الأسعار":
    st.markdown('<div class="pt">⚖️ مقارنة الأسعار</div><div class="ps">نفس المنتج من متاجر مختلفة</div>', unsafe_allow_html=True)

    if not groups:
        st.warning("لا توجد بيانات مطابقة")
    else:
        q = st.text_input("🔍 ابحث عن منتج")
        filtered_groups = [g for g in groups if not q or q.lower() in g["canonical_name"].lower()]
        st.caption(f"**{len(filtered_groups)}** مجموعة")

        for g in filtered_groups[:50]:
            short = g['canonical_name'][:38] + ("..." if len(g['canonical_name']) > 38 else "")
            with st.expander(f"📦 {short} — أفضل: {g['best_price']} KD"):
                rows = [
                    {"✔": "✅" if p["price"] == g["best_price"] else "",
                     "المتجر": p["store"], "السعر (KD)": p["price"]}
                    for p in g["products"]
                ]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════
# 🏆 أفضل العروض
# ══════════════════════════════════════════════════════════════════
elif page == "🏆 أفضل العروض":
    st.markdown('<div class="pt">🏆 أفضل العروض</div><div class="ps">أكبر فارق سعري بين المتاجر</div>', unsafe_allow_html=True)

    if not groups:
        st.warning("لا توجد بيانات")
    else:
        min_save = st.slider("الحد الأدنى للتوفير (%)", 0, 100, 10)
        deals = [g for g in sorted(groups, key=lambda g: g.get("savings_pct", 0), reverse=True)
                 if g.get("savings_pct", 0) >= min_save]
        st.caption(f"**{len(deals)}** عرض")

        if deals:
            dd = pd.DataFrame([{
                "المنتج":    g["canonical_name"][:45],
                "أفضل سعر": f"{g['best_price']} KD",
                "توفير":     f"{g['savings_pct']}%",
            } for g in deals[:100]])
            st.dataframe(dd, use_container_width=True, hide_index=True)

            if len(deals) >= 3:
                st.markdown("---")
                st.markdown("**أفضل 20 عرضاً**")
                cd = pd.DataFrame([{"المنتج": g["canonical_name"][:30], "توفير %": g["savings_pct"]}
                                    for g in deals[:20]])
                bar = (
                    alt.Chart(cd)
                    .mark_bar(color="#2563eb", cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
                    .encode(
                        x=alt.X("توفير %:Q", axis=alt.Axis(labelFont="Cairo", labelFontSize=11)),
                        y=alt.Y("المنتج:N", sort="-x", axis=alt.Axis(labelFont="Cairo", labelFontSize=10)),
                        tooltip=["المنتج", "توفير %"],
                    )
                    .properties(height=450)
                    .configure_axis(labelFont="Cairo", labelFontSize=11)
                )
                st.altair_chart(bar, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# 🤖 توصيف الأعمال
# ══════════════════════════════════════════════════════════════════
elif page == "🤖 توصيف الأعمال":
    st.markdown('<div class="pt">🤖 توصيف الأعمال</div><div class="ps">بنود أعمال الكهرباء بالذكاء الاصطناعي</div>', unsafe_allow_html=True)

    if not api_key:
        st.warning("⚠️ مفتاح Anthropic API غير موجود — أضفه في ملف `.env` أو في Streamlit Secrets باسم `ANTHROPIC_API_KEY`")

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
            (k1, "📋", "blue",   len(wi),                          "البنود"),
            (k2, "📂", "teal",   len(cats),                        "الفئات"),
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
                "الوصف": i.get("description", "")[:55],
                "السعر": f"{i.get('min_price','—')} - {i.get('max_price','—')} KD",
            } for n, i in enumerate(fi)])
            st.dataframe(td, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════
# 📈 تاريخ الأسعار
# ══════════════════════════════════════════════════════════════════
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
                .mark_line(point=True, strokeWidth=2)
                .encode(
                    x=alt.X("timestamp:T", title="التاريخ",   axis=alt.Axis(labelFont="Cairo", labelFontSize=10)),
                    y=alt.Y("price:Q",     title="السعر (KD)", axis=alt.Axis(labelFont="Cairo", labelFontSize=10)),
                    color=alt.Color("store:N", legend=alt.Legend(labelFont="Cairo", labelFontSize=10)),
                    tooltip=["store", "price", "timestamp"],
                )
                .properties(height=350)
                .configure_axis(labelFont="Cairo", labelFontSize=10)
                .configure_legend(labelFont="Cairo", labelFontSize=10)
            )
            st.altair_chart(line, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# 📊 الرسوم البيانية
# ══════════════════════════════════════════════════════════════════
elif page == "📊 الرسوم البيانية":
    st.markdown('<div class="pt">📊 الرسوم البيانية</div><div class="ps">تحليل بصري للأسعار والمتاجر</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات")
    else:
        r1c1, r1c2 = st.columns(2)

        with r1c1:
            st.markdown("**توزيع الأسعار**")
            hist = (
                alt.Chart(df)
                .mark_bar(color="#2563eb", opacity=.8)
                .encode(
                    alt.X("price:Q", bin=alt.Bin(maxbins=35), axis=alt.Axis(labelFont="Cairo", labelFontSize=10)),
                    alt.Y("count()",                           axis=alt.Axis(labelFont="Cairo", labelFontSize=10)),
                )
                .properties(height=300)
                .configure_axis(labelFont="Cairo", labelFontSize=10)
            )
            st.altair_chart(hist, use_container_width=True)

        with r1c2:
            st.markdown("**متوسط السعر حسب المتجر**")
            avg_df = df.groupby("store")["price"].mean().reset_index()
            ab = (
                alt.Chart(avg_df)
                .mark_bar(color="#0d9488", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X("store:N", title="", axis=alt.Axis(labelFont="Cairo", labelFontSize=10)),
                    y=alt.Y("price:Q",           axis=alt.Axis(labelFont="Cairo", labelFontSize=10)),
                    tooltip=["store", "price"],
                )
                .properties(height=300)
                .configure_axis(labelFont="Cairo", labelFontSize=10)
            )
            st.altair_chart(ab, use_container_width=True)
