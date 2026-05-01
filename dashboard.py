import streamlit as st
import pandas as pd
import altair as alt
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------
# إعداد الصفحة
# ---------------------------------------------------------------
st.set_page_config(
    page_title="مقارنة الأسعار الكهربائية - الكويت",
    page_icon="⚡",
    layout="wide",
)

# ---------------------------------------------------------------
# CSS — تصميم احترافي هادئ (Gamma-style)
# ---------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;900&display=swap');

/* ── متغيرات التصميم ── */
:root {
    --bg:        #f6f8fb;
    --surface:   #ffffff;
    --border:    #e4e9f0;
    --primary:   #2563eb;
    --primary-d: #1d4ed8;
    --success:   #059669;
    --success-l: #d1fae5;
    --purple:    #7c3aed;
    --purple-l:  #ede9fe;
    --amber:     #d97706;
    --amber-l:   #fef3c7;
    --text-1:    #0f172a;
    --text-2:    #475569;
    --text-3:    #94a3b8;
    --radius-sm: 8px;
    --radius:    12px;
    --radius-lg: 18px;
    --shadow-sm: 0 1px 3px rgba(15,23,42,.06), 0 1px 2px rgba(15,23,42,.04);
    --shadow:    0 4px 16px rgba(15,23,42,.08), 0 1px 4px rgba(15,23,42,.04);
    --shadow-lg: 0 12px 32px rgba(15,23,42,.10), 0 2px 8px rgba(15,23,42,.06);
}

/* ── القاعدة ── */
html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
    background: var(--bg);
    color: var(--text-1);
}

/* ── إزالة padding افتراضي Streamlit ── */
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
section[data-testid="stSidebar"] { background: var(--surface) !important; border-left: 1px solid var(--border); }

/* ══════════════════════════════
   HEADER
══════════════════════════════ */
.main-header {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 32px 40px;
    margin-bottom: 28px;
    text-align: center;
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(37,99,235,.06) 0%, rgba(124,58,237,.04) 100%);
    pointer-events: none;
}
.main-header .header-icon {
    font-size: 2.6rem;
    display: block;
    margin-bottom: 8px;
    line-height: 1;
}
.main-header h1 {
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--text-1);
    margin: 0 0 6px;
    letter-spacing: -.02em;
}
.main-header p {
    font-size: 0.95rem;
    color: var(--text-2);
    margin: 0;
    font-weight: 400;
}
.header-tag {
    display: inline-block;
    background: var(--primary);
    color: white;
    border-radius: 20px;
    padding: 2px 14px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-bottom: 14px;
}

/* ══════════════════════════════
   KPI CARDS
══════════════════════════════ */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 16px 18px;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .18s, transform .18s;
    position: relative;
    overflow: hidden;
}
.kpi-card:hover { box-shadow: var(--shadow); transform: translateY(-2px); }
.kpi-card::after {
    content: "";
    position: absolute;
    bottom: 0; right: 0; left: 0;
    height: 3px;
    background: var(--primary);
    border-radius: 0 0 var(--radius) var(--radius);
}
.kpi-card.green::after  { background: var(--success); }
.kpi-card.purple::after { background: var(--purple); }
.kpi-card.amber::after  { background: var(--amber); }
.kpi-card .kpi-icon  { font-size: 1.5rem; margin-bottom: 6px; line-height: 1; }
.kpi-card .kpi-value { font-size: 2rem; font-weight: 700; color: var(--text-1); line-height: 1.1; }
.kpi-card .kpi-label { font-size: 0.82rem; color: var(--text-2); margin-top: 5px; font-weight: 400; }

/* ══════════════════════════════
   DEAL CARDS
══════════════════════════════ */
.deal-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 18px;
    margin-bottom: 10px;
    box-shadow: var(--shadow-sm);
    display: flex;
    align-items: center;
    gap: 12px;
    transition: box-shadow .15s;
}
.deal-card:hover { box-shadow: var(--shadow); }
.deal-card .deal-rank {
    background: var(--primary);
    color: white;
    border-radius: 50%;
    width: 28px; height: 28px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 700;
    flex-shrink: 0;
}
.deal-card .deal-rank.gold   { background: #d97706; }
.deal-card .deal-rank.silver { background: #94a3b8; }
.deal-card .deal-rank.bronze { background: #b45309; }
.deal-card .deal-body { flex: 1; }
.deal-card .deal-name  { font-weight: 600; font-size: 0.95rem; color: var(--text-1); }
.deal-card .deal-store { font-size: 0.82rem; color: var(--text-2); margin-top: 2px; }
.deal-card .deal-price { text-align: left; }
.deal-card .deal-kd    { font-weight: 700; color: var(--primary); font-size: 1rem; }

/* ══════════════════════════════
   WORK ITEM CARDS
══════════════════════════════ */
.work-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 18px;
    margin-bottom: 10px;
    box-shadow: var(--shadow-sm);
    border-right: 4px solid var(--purple);
    transition: box-shadow .15s;
}
.work-card:hover { box-shadow: var(--shadow); }
.work-card .work-desc     { font-weight: 600; font-size: 0.97rem; color: var(--text-1); margin: 6px 0 4px; }
.work-card .work-price    { font-size: 0.88rem; color: var(--text-2); margin-top: 2px; }
.work-card .work-price strong { color: var(--success); }

/* ══════════════════════════════
   BADGES
══════════════════════════════ */
.badge {
    display: inline-block;
    border-radius: 20px;
    padding: 2px 11px;
    font-size: 0.76rem;
    font-weight: 600;
    line-height: 1.6;
}
.badge-green  { background: var(--success-l); color: #065f46; }
.badge-blue   { background: #dbeafe; color: #1e40af; }
.badge-purple { background: var(--purple-l); color: #5b21b6; }
.badge-amber  { background: var(--amber-l);  color: #92400e; }
.badge-white  { background: rgba(255,255,255,.15); color: white; border: 1px solid rgba(255,255,255,.25); }

/* ══════════════════════════════
   SECTION TITLE
══════════════════════════════ */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-1);
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}

/* ══════════════════════════════
   INFO BOX
══════════════════════════════ */
.info-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-right: 4px solid var(--primary);
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    margin-bottom: 14px;
    color: #1e3a8a;
    font-size: 0.9rem;
    line-height: 1.6;
}

/* ══════════════════════════════
   PAGE TITLE
══════════════════════════════ */
.page-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-1);
    margin-bottom: 4px;
}
.page-subtitle {
    font-size: 0.9rem;
    color: var(--text-2);
    margin-bottom: 24px;
}

/* ══════════════════════════════
   STORE TABLE
══════════════════════════════ */
.store-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.92rem;
}
.store-table th {
    background: #f1f5f9 !important;
    color: var(--text-2) !important;
    font-weight: 600;
    padding: 10px 14px;
    text-align: right;
    border-bottom: 1px solid var(--border);
}
.store-table td {
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    color: var(--text-1);
}
.store-table tr:last-child td { border-bottom: none; }
.store-table tr:hover td { background: #f8fafc; }

/* ── الـ sidebar ── */
.sidebar-logo {
    text-align: center;
    padding: 8px 0 16px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
}
.sidebar-logo .s-icon { font-size: 2rem; }
.sidebar-logo .s-title { font-size: 1rem; font-weight: 700; color: var(--text-1); margin: 4px 0 2px; }
.sidebar-logo .s-sub   { font-size: 0.78rem; color: var(--text-3); }

/* ── إجبار ألوان الـ Sidebar ── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
    color: #0f172a !important;
    font-family: 'Cairo', sans-serif !important;
}
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #475569 !important;
    font-size: 0.82rem !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #e4e9f0 !important;
    margin: 12px 0 !important;
}
.sidebar-stat {
    background: #f8fafc;
    border: 1px solid #e4e9f0;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #0f172a;
}
.sidebar-stat .stat-label { color: #475569; font-size: 0.78rem; }
.sidebar-stat .stat-val   { font-weight: 700; font-size: 1rem; color: #2563eb; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# تحميل البيانات
# ---------------------------------------------------------------
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


# ---------------------------------------------------------------
# تشغيل التحديث اليدوي
# ---------------------------------------------------------------
def run_update(run_ai: bool = False):
    steps = [BASE_DIR / "scraper.py", BASE_DIR / "matcher.py"]
    if run_ai:
        steps.append(BASE_DIR / "ai_agent.py")

    label = "جاري تحديث البيانات" + (" وتوليد توصيف الأعمال بالذكاء الاصطناعي" if run_ai else "")
    with st.spinner(f"{label} ... قد يستغرق هذا بضع دقائق"):
        try:
            for script in steps:
                subprocess.run(
                    [sys.executable, str(script)],
                    timeout=600,
                    check=True,
                    capture_output=True,
                )
            reload_all()
            st.success("تم التحديث بنجاح!")
            st.rerun()
        except subprocess.CalledProcessError as e:
            st.error(f"فشل التحديث: {e.stderr.decode() if e.stderr else str(e)}")
        except subprocess.TimeoutExpired:
            st.error("انتهت مهلة التحديث. يرجى المحاولة لاحقاً.")


def run_ai_only():
    with st.spinner("عميل الذكاء الاصطناعي يحلل المنتجات ... قد يستغرق عدة دقائق"):
        try:
            subprocess.run(
                [sys.executable, str(BASE_DIR / "ai_agent.py")],
                timeout=600,
                check=True,
                capture_output=True,
            )
            reload_all()
            st.success("تم توليد توصيف الأعمال بنجاح!")
            st.rerun()
        except subprocess.CalledProcessError as e:
            st.error(f"فشل عميل الذكاء الاصطناعي: {e.stderr.decode() if e.stderr else str(e)}")
        except subprocess.TimeoutExpired:
            st.error("انتهت مهلة العميل.")


# ---------------------------------------------------------------
# بدء الجدول الزمني (في الخلفية)
# ---------------------------------------------------------------
if "scheduler_started" not in st.session_state:
    try:
        from scheduler import start_scheduler
        st.session_state["scheduler"] = start_scheduler()
        st.session_state["scheduler_started"] = True
    except Exception:
        st.session_state["scheduler_started"] = False


# ---------------------------------------------------------------
# تحميل البيانات
# ---------------------------------------------------------------
df = load_products()
groups = load_groups()
history_df = load_history()
work_data = load_work_descriptions()


# ---------------------------------------------------------------
# الشريط الجانبي
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚡ مقارنة الأسعار")
    st.caption("المتاجر الكهربائية — الكويت")
    st.divider()

    page = st.radio(
        "الصفحات",
        [
            "🏠 الرئيسية",
            "📦 المنتجات",
            "⚖️ مقارنة الأسعار",
            "🏆 أفضل العروض",
            "🤖 توصيف الأعمال الكهربائية",
            "📈 تاريخ الأسعار",
            "📊 الرسوم البيانية",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    if st.button("🔄 تحديث البيانات", use_container_width=True):
        run_update(run_ai=False)

    if st.button("🤖 تحديث + AI", use_container_width=True, type="primary"):
        run_update(run_ai=True)

    if st.button("♻️ مسح الكاش", use_container_width=True):
        reload_all()
        st.rerun()

    st.divider()

    # إحصائيات
    store_count = df["store"].nunique() if not df.empty else 0
    work_items_count = len(work_data.get("work_items", []))
    scheduler_ok = st.session_state.get("scheduler_started", False)

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("المنتجات", f"{len(df):,}")
        st.metric("التوصيف", work_items_count)
    with col_b:
        st.metric("المتاجر", store_count)
        st.metric("المطابقة", len(groups))

    st.caption(f"الجدول: {'✅ يعمل' if scheduler_ok else '⚠️ متوقف'}")

    if not df.empty and "timestamp" in df.columns:
        last_ts = df["timestamp"].max()
        st.caption(f"آخر تحديث: {last_ts}")

    if work_data:
        gen_at = work_data.get("generated_at", "")
        if gen_at:
            try:
                gen_dt = datetime.fromisoformat(gen_at).strftime("%Y-%m-%d %H:%M")
            except ValueError:
                gen_dt = gen_at
            st.caption(f"توليد AI: {gen_dt}")


# ===============================================================
# صفحة الرئيسية
# ===============================================================
if page == "🏠 الرئيسية":
    st.markdown("""
    <div class="main-header">
        <span class="header-icon">⚡</span>
        <div class="header-tag">الكويت</div>
        <h1>مقارنة الأسعار الكهربائية</h1>
        <p>منصة ذكية لمتابعة أسعار المتاجر الكهربائية الكويتية مع توصيف أعمال بالذكاء الاصطناعي</p>
    </div>
    """, unsafe_allow_html=True)

    # تحذير إذا البيانات فاضية
    if df.empty:
        st.warning(
            f"⚠️ لا توجد بيانات محملة. "
            f"الملف المتوقع: `{BASE_DIR / 'products_all.json'}`\n\n"
            "**الحل:** اضغط زر **🔄 تحديث البيانات** في الشريط الجانبي، "
            "أو شغّل: `python3 scraper.py` ثم `python3 matcher.py`"
        )

    work_items_count = len(work_data.get("work_items", []))
    avg_saving = round(sum(g.get("savings_pct", 0) for g in groups) / len(groups), 1) if groups else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📦</div>
            <div class="kpi-value">{len(df):,}</div>
            <div class="kpi-label">إجمالي المنتجات</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card green">
            <div class="kpi-icon">🏪</div>
            <div class="kpi-value">{df["store"].nunique() if not df.empty else 0}</div>
            <div class="kpi-label">عدد المتاجر</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">⚖️</div>
            <div class="kpi-value">{len(groups)}</div>
            <div class="kpi-label">منتجات مقارنة</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card amber">
            <div class="kpi-icon">💰</div>
            <div class="kpi-value">{avg_saving}%</div>
            <div class="kpi-label">متوسط التوفير</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card purple">
            <div class="kpi-icon">🤖</div>
            <div class="kpi-value">{work_items_count}</div>
            <div class="kpi-label">بنود التوصيف</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # أفضل العروض
    if groups:
        st.markdown('<div class="section-title">🏆 أبرز العروض اليوم</div>', unsafe_allow_html=True)
        top5 = sorted(groups, key=lambda g: g.get("savings_pct", 0), reverse=True)[:5]
        rank_classes = ["gold", "silver", "bronze", "", ""]
        for i, g in enumerate(top5):
            rank_cls = rank_classes[i] if i < len(rank_classes) else ""
            st.markdown(f"""
            <div class="deal-card">
                <div class="deal-rank {rank_cls}">{i+1}</div>
                <div class="deal-body">
                    <div class="deal-name">{g['canonical_name']}</div>
                    <div class="deal-store">🏪 {g['best_store']}</div>
                </div>
                <div class="deal-price">
                    <div class="deal-kd">{g['best_price']} KD</div>
                    <span class="badge badge-green">توفير {g['savings_pct']}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # أبرز بنود التوصيف
    if work_data.get("work_items"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">🤖 أبرز بنود توصيف الأعمال &nbsp;<span class="badge badge-purple">AI</span></div>', unsafe_allow_html=True)
        items_preview = work_data["work_items"][:5]
        for item in items_preview:
            st.markdown(f"""
            <div class="work-card">
                <span class="badge badge-purple">{item.get("category", "")}</span>
                <div class="work-desc">{item.get("description", "")}</div>
                <div class="work-price">
                    أدنى: <strong>{item.get("min_price", "—")} KD</strong> &nbsp;·&nbsp;
                    متوسط: <strong>{item.get("avg_price", "—")} KD</strong> &nbsp;·&nbsp;
                    أعلى: <strong>{item.get("max_price", "—")} KD</strong>
                    &nbsp;&nbsp;<span class="badge badge-blue">🏪 {item.get("best_store", "—")}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # توزيع المتاجر
    if not df.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">🏪 المتاجر المتاحة</div>', unsafe_allow_html=True)
        store_counts = df.groupby("store").size().reset_index(name="عدد المنتجات")
        store_counts.columns = ["المتجر", "عدد المنتجات"]
        st.dataframe(store_counts, use_container_width=True, hide_index=True)


# ===============================================================
# صفحة المنتجات
# ===============================================================
elif page == "📦 المنتجات":
    st.markdown('<div class="page-title">📦 قائمة المنتجات</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">تصفح وابحث في جميع المنتجات المجلوبة من المتاجر الكهربائية</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات. اضغط 'تحديث البيانات الآن' من الشريط الجانبي.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            search = st.text_input("🔍 بحث باسم المنتج")

        with col2:
            stores = ["الكل"] + sorted(df["store"].unique().tolist())
            selected_store = st.selectbox("🏪 المتجر", stores)

        with col3:
            min_p = float(df["price"].min())
            max_p = float(df["price"].max())
            if min_p == max_p:
                price_range = (min_p, max_p)
            else:
                price_range = st.slider("💰 نطاق السعر (KD)", min_value=min_p, max_value=max_p, value=(min_p, max_p))

        filtered = df.copy()
        if search:
            filtered = filtered[filtered["name"].str.contains(search, case=False, na=False)]
        if selected_store != "الكل":
            filtered = filtered[filtered["store"] == selected_store]
        filtered = filtered[(filtered["price"] >= price_range[0]) & (filtered["price"] <= price_range[1])]

        st.write(f"يُعرض **{len(filtered)}** منتج")

        display_cols = [c for c in ["name", "price", "store", "url", "timestamp"] if c in filtered.columns]
        col_labels = {
            "name": "اسم المنتج",
            "price": "السعر (KD)",
            "store": "المتجر",
            "url": "رابط",
            "timestamp": "وقت الجلب",
        }
        show_df = filtered[display_cols].rename(columns=col_labels)
        st.dataframe(show_df, use_container_width=True, hide_index=True)

        csv = filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ تحميل CSV", csv, "products.csv", "text/csv")


# ===============================================================
# صفحة مقارنة الأسعار
# ===============================================================
elif page == "⚖️ مقارنة الأسعار":
    st.markdown('<div class="page-title">⚖️ مقارنة الأسعار بين المتاجر</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">منتجات متطابقة من متاجر مختلفة مع تمييز الأرخص</div>', unsafe_allow_html=True)

    if not groups:
        st.warning("لا توجد بيانات مقارنة. شغّل التحديث أولاً.")
    else:
        search_compare = st.text_input("🔍 ابحث عن منتج للمقارنة")

        filtered_groups = [
            g for g in groups
            if not search_compare or search_compare.lower() in g["canonical_name"].lower()
        ]

        st.write(f"عدد المنتجات المتطابقة: **{len(filtered_groups)}**")

        for g in filtered_groups[:50]:
            with st.expander(
                f"📦 {g['canonical_name']} — أفضل سعر: {g['best_price']} KD ({g['best_store']}) | توفير {g['savings_pct']}%"
            ):
                rows = []
                for p in g["products"]:
                    is_best = p["price"] == g["best_price"]
                    rows.append({
                        "المتجر": p["store"],
                        "اسم المنتج": p["name"],
                        "السعر (KD)": p["price"],
                        "الرابط": p.get("url", ""),
                        "": "✅ الأرخص" if is_best else "",
                    })
                comparison_df = pd.DataFrame(rows)

                def color_row(row):
                    if row.get("") == "✅ الأرخص":
                        return ["background-color: #c6f6d5"] * len(row)
                    return [""] * len(row)

                st.dataframe(
                    comparison_df.style.apply(color_row, axis=1),
                    use_container_width=True,
                    hide_index=True,
                )


# ===============================================================
# صفحة أفضل العروض
# ===============================================================
elif page == "🏆 أفضل العروض":
    st.markdown('<div class="page-title">🏆 أفضل العروض</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">المنتجات ذات أكبر فارق سعري بين المتاجر</div>', unsafe_allow_html=True)

    if not groups:
        st.warning("لا توجد بيانات. شغّل التحديث أولاً.")
    else:
        sorted_groups = sorted(groups, key=lambda g: g.get("savings_pct", 0), reverse=True)

        min_saving = st.slider("الحد الأدنى لنسبة التوفير (%)", 0, 100, 10)
        filtered_deals = [g for g in sorted_groups if g.get("savings_pct", 0) >= min_saving]

        st.write(f"عدد العروض: **{len(filtered_deals)}**")

        if filtered_deals:
            deals_data = [
                {
                    "المنتج": g["canonical_name"],
                    "أفضل سعر (KD)": g["best_price"],
                    "أغلى سعر (KD)": g["worst_price"],
                    "أفضل متجر": g["best_store"],
                    "نسبة التوفير": f"{g['savings_pct']}%",
                }
                for g in filtered_deals[:100]
            ]
            deals_df = pd.DataFrame(deals_data)
            st.dataframe(deals_df, use_container_width=True, hide_index=True)

            csv = deals_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("⬇️ تحميل CSV", csv, "best_deals.csv", "text/csv")

            st.markdown("---")
            st.subheader("أفضل 20 عرضاً")
            chart_data = pd.DataFrame([
                {"المنتج": g["canonical_name"][:40], "توفير %": g["savings_pct"]}
                for g in filtered_deals[:20]
            ])

            bar = (
                alt.Chart(chart_data)
                .mark_bar(color="#38a169")
                .encode(
                    x=alt.X("توفير %:Q", title="نسبة التوفير %"),
                    y=alt.Y("المنتج:N", sort="-x", title=""),
                    tooltip=["المنتج", "توفير %"],
                )
                .properties(height=500)
            )
            st.altair_chart(bar, use_container_width=True)


# ===============================================================
# صفحة توصيف الأعمال الكهربائية (AI)
# ===============================================================
elif page == "🤖 توصيف الأعمال الكهربائية":
    st.markdown("""
    <div class="page-title">🤖 توصيف الأعمال الكهربائية &nbsp;<span class="badge badge-purple">مدعوم بـ Claude AI</span></div>
    <div class="page-subtitle">بنود أعمال الكهرباء المولّدة تلقائياً بالذكاء الاصطناعي بناءً على أسعار السوق</div>
    """, unsafe_allow_html=True)

    if not work_data or not work_data.get("work_items"):
        st.markdown("""
        <div class="info-box">
            لم يتم توليد بنود التوصيف بعد. اضغط الزر أدناه لتشغيل عميل الذكاء الاصطناعي وتحليل المنتجات.
            <br><strong>تأكد من تعيين متغير البيئة ANTHROPIC_API_KEY قبل التشغيل.</strong>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 تشغيل عميل الذكاء الاصطناعي الآن", use_container_width=True):
            run_ai_only()
    else:
        work_items = work_data.get("work_items", [])
        categories_summary = work_data.get("categories_summary", {})
        generated_at = work_data.get("generated_at", "")
        products_analyzed = work_data.get("products_analyzed", 0)

        # معلومات عامة
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{len(work_items)}</div>
                <div class="kpi-label">بنود التوصيف</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{len(categories_summary)}</div>
                <div class="kpi-label">فئات العمل</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{products_analyzed:,}</div>
                <div class="kpi-label">منتجات تم تحليلها</div>
            </div>
            """, unsafe_allow_html=True)

        if generated_at:
            try:
                gen_str = datetime.fromisoformat(generated_at).strftime("%Y-%m-%d %H:%M")
            except ValueError:
                gen_str = generated_at
            st.caption(f"تاريخ التوليد: {gen_str}")

        st.markdown("<br>", unsafe_allow_html=True)

        # فلاتر
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            search_work = st.text_input("🔍 بحث في بنود التوصيف")
        with col_f2:
            all_categories = ["الكل"] + sorted(categories_summary.keys())
            selected_cat = st.selectbox("📂 الفئة", all_categories)
        with col_f3:
            all_stores_work = ["الكل"] + sorted({item.get("best_store", "") for item in work_items if item.get("best_store")})
            selected_store_work = st.selectbox("🏪 أفضل متجر", all_stores_work)

        # تصفية البنود
        filtered_items = work_items
        if search_work:
            filtered_items = [
                i for i in filtered_items
                if search_work.lower() in i.get("description", "").lower()
                or search_work.lower() in i.get("category", "").lower()
            ]
        if selected_cat != "الكل":
            filtered_items = [i for i in filtered_items if i.get("category") == selected_cat]
        if selected_store_work != "الكل":
            filtered_items = [i for i in filtered_items if i.get("best_store") == selected_store_work]

        st.write(f"يُعرض **{len(filtered_items)}** بند")

        # عرض الجدول
        if filtered_items:
            table_data = [
                {
                    "رقم البند": item.get("item_no", i + 1),
                    "وصف العمل": item.get("description", ""),
                    "الوحدة": item.get("unit", ""),
                    "أدنى سعر (KD)": item.get("min_price", ""),
                    "متوسط السعر (KD)": item.get("avg_price", ""),
                    "أعلى سعر (KD)": item.get("max_price", ""),
                    "أفضل متجر": item.get("best_store", ""),
                    "الفئة": item.get("category", ""),
                }
                for i, item in enumerate(filtered_items)
            ]
            table_df = pd.DataFrame(table_data)
            st.dataframe(table_df, use_container_width=True, hide_index=True)

            csv = table_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("⬇️ تحميل توصيف الأعمال CSV", csv, "work_descriptions.csv", "text/csv")

        # ملخص الفئات
        if categories_summary:
            st.markdown("---")
            st.markdown('<div class="section-title">📊 ملخص الفئات</div>', unsafe_allow_html=True)
            cat_df = pd.DataFrame(
                [{"الفئة": k, "عدد البنود": v} for k, v in categories_summary.items()]
            ).sort_values("عدد البنود", ascending=False)

            cat_chart = (
                alt.Chart(cat_df)
                .mark_bar(color="#4263eb")
                .encode(
                    x=alt.X("عدد البنود:Q", title="عدد البنود"),
                    y=alt.Y("الفئة:N", sort="-x", title=""),
                    tooltip=["الفئة", "عدد البنود"],
                )
                .properties(height=350)
            )
            st.altair_chart(cat_chart, use_container_width=True)

        st.markdown("---")
        if st.button("🔄 إعادة تشغيل عميل الذكاء الاصطناعي", use_container_width=False):
            run_ai_only()


# ===============================================================
# صفحة تاريخ الأسعار
# ===============================================================
elif page == "📈 تاريخ الأسعار":
    st.markdown('<div class="page-title">📈 تاريخ الأسعار</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">تتبع تغير سعر أي منتج عبر الزمن</div>', unsafe_allow_html=True)

    if history_df.empty:
        st.warning("لا توجد بيانات تاريخية بعد. سيتم تجميعها تلقائياً عند كل تحديث.")
    else:
        product_names = sorted(history_df["name"].unique().tolist())
        selected_product = st.selectbox("اختر منتجاً لعرض تاريخ سعره:", product_names)

        if selected_product:
            product_history = history_df[history_df["name"] == selected_product].sort_values("timestamp")

            line = (
                alt.Chart(product_history)
                .mark_line(point=True)
                .encode(
                    x=alt.X("timestamp:T", title="التاريخ"),
                    y=alt.Y("price:Q", title="السعر (KD)"),
                    color=alt.Color("store:N", title="المتجر"),
                    tooltip=["store", "price", "timestamp"],
                )
                .properties(height=400, title=f"تاريخ سعر: {selected_product}")
            )
            st.altair_chart(line, use_container_width=True)

            st.markdown("---")
            st.subheader("جدول البيانات التاريخية")
            show = product_history[["timestamp", "store", "price"]].rename(
                columns={"timestamp": "التاريخ", "store": "المتجر", "price": "السعر (KD)"}
            )
            st.dataframe(show, use_container_width=True, hide_index=True)


# ===============================================================
# صفحة الرسوم البيانية
# ===============================================================
elif page == "📊 الرسوم البيانية":
    st.markdown('<div class="page-title">📊 الرسوم البيانية</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">تحليل بصري شامل للأسعار والمتاجر</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("لا توجد بيانات.")
    else:
        # 1) توزيع الأسعار
        st.subheader("توزيع الأسعار")
        hist = (
            alt.Chart(df)
            .mark_bar(color="#A3C4F3")
            .encode(
                alt.X("price:Q", bin=alt.Bin(maxbins=40), title="السعر (KD)"),
                alt.Y("count()", title="عدد المنتجات"),
            )
            .properties(height=300)
        )
        st.altair_chart(hist, use_container_width=True)

        # 2) متوسط السعر لكل متجر
        st.subheader("متوسط السعر لكل متجر")
        avg_df = df.groupby("store")["price"].mean().reset_index()
        bar = (
            alt.Chart(avg_df)
            .mark_bar(color="#F7A4A4")
            .encode(
                x=alt.X("store:N", title="المتجر"),
                y=alt.Y("price:Q", title="متوسط السعر (KD)"),
                tooltip=["store", "price"],
            )
            .properties(height=300)
        )
        st.altair_chart(bar, use_container_width=True)

        # 3) أرخص 20 منتج
        st.subheader("أرخص 20 منتج")
        top20 = df.sort_values("price").head(20)
        hbar = (
            alt.Chart(top20)
            .mark_bar(color="#C1E1C1")
            .encode(
                x=alt.X("price:Q", title="السعر (KD)"),
                y=alt.Y("name:N", sort="x", title="المنتج"),
                color=alt.Color("store:N", title="المتجر"),
                tooltip=["name", "price", "store"],
            )
            .properties(height=500)
        )
        st.altair_chart(hbar, use_container_width=True)

        # 4) مخطط الصندوق لكل متجر
        st.subheader("توزيع الأسعار لكل متجر (Box Plot)")
        box_chart = (
            alt.Chart(df)
            .mark_boxplot(color="#A0C4FF")
            .encode(
                x=alt.X("store:N", title="المتجر"),
                y=alt.Y("price:Q", title="السعر (KD)"),
                tooltip=["store", "price"],
            )
            .properties(height=350)
        )
        st.altair_chart(box_chart, use_container_width=True)

        # 5) نطاق الأسعار لكل متجر
        st.subheader("نطاق الأسعار لكل متجر")
        range_df = df.groupby("store")["price"].agg(["min", "max"]).reset_index()
        range_chart = (
            alt.Chart(range_df)
            .mark_rule(color="#BDB2FF", strokeWidth=4)
            .encode(
                x="store:N",
                y="min:Q",
                y2="max:Q",
                tooltip=["store", "min", "max"],
            )
            .properties(height=300)
        )
        st.altair_chart(range_chart, use_container_width=True)

        # 6) درجة استقرار الأسعار
        st.subheader("درجة استقرار الأسعار لكل متجر")
        score_df = df.groupby("store")["price"].var().reset_index()
        score_df["price"] = score_df["price"].fillna(0)
        score_df["score"] = 1 / (1 + score_df["price"])
        score_chart = (
            alt.Chart(score_df)
            .mark_bar(color="#FDCFE8")
            .encode(
                x="store:N",
                y=alt.Y("score:Q", title="درجة الاستقرار"),
                tooltip=["store", "score"],
            )
            .properties(height=300)
        )
        st.altair_chart(score_chart, use_container_width=True)
