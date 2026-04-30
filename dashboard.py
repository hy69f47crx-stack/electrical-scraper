import streamlit as st
import pandas as pd
import altair as alt
import json
import subprocess
import sys
from datetime import datetime

# ---------------------------------------------------------------
# إعداد الصفحة
# ---------------------------------------------------------------
st.set_page_config(
    page_title="مقارنة الأسعار الكهربائية - الكويت",
    page_icon="⚡",
    layout="wide",
)

# ---------------------------------------------------------------
# CSS — دعم RTL + تصميم عربي احترافي
# ---------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
}

.main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 24px 32px;
    border-radius: 16px;
    color: white;
    margin-bottom: 24px;
    text-align: center;
}

.main-header h1 { font-size: 2rem; margin: 0; color: #e0e0e0; }
.main-header p  { font-size: 1rem; margin: 8px 0 0; color: #a0aec0; }

.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border-top: 4px solid #0f3460;
}
.kpi-card .kpi-value { font-size: 2rem; font-weight: 700; color: #0f3460; }
.kpi-card .kpi-label { font-size: 0.9rem; color: #718096; margin-top: 4px; }

.best-deal-card {
    background: linear-gradient(135deg, #f0fff4, #c6f6d5);
    border-radius: 12px;
    padding: 16px;
    border-left: 4px solid #38a169;
    margin-bottom: 10px;
}

.saving-badge {
    background: #38a169;
    color: white;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.85rem;
    font-weight: 700;
}

.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #2d3748;
    border-bottom: 3px solid #0f3460;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

.update-btn button {
    background: #0f3460 !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 8px 20px !important;
    font-family: 'Cairo', sans-serif !important;
}

table { width: 100%; }
th { background: #0f3460 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# تحميل البيانات
# ---------------------------------------------------------------
@st.cache_data(ttl=300)
def load_products():
    try:
        with open("products_all.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df.dropna(subset=["price"])
        return df
    except (FileNotFoundError, ValueError, KeyError):
        return pd.DataFrame(columns=["name", "price", "store", "url", "timestamp", "currency"])


@st.cache_data(ttl=300)
def load_groups():
    try:
        with open("matched_groups.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return []


@st.cache_data(ttl=300)
def load_history():
    try:
        with open("price_history.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        return df.dropna(subset=["price", "timestamp"])
    except (FileNotFoundError, ValueError):
        return pd.DataFrame(columns=["name", "price", "store", "timestamp"])


def reload_data():
    load_products.clear()
    load_groups.clear()
    load_history.clear()


# ---------------------------------------------------------------
# تشغيل التحديث اليدوي
# ---------------------------------------------------------------
def run_update():
    with st.spinner("جاري تحديث البيانات ... قد يستغرق هذا بضع دقائق"):
        try:
            subprocess.run(
                [sys.executable, "scraper.py"],
                timeout=600,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [sys.executable, "matcher.py"],
                timeout=120,
                check=True,
                capture_output=True,
            )
            reload_data()
            st.success("تم التحديث بنجاح!")
            st.rerun()
        except subprocess.CalledProcessError as e:
            st.error(f"فشل التحديث: {e.stderr.decode() if e.stderr else str(e)}")
        except subprocess.TimeoutExpired:
            st.error("انتهت مهلة التحديث. يرجى المحاولة لاحقاً.")


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


# ---------------------------------------------------------------
# الشريط الجانبي
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚡ القائمة الرئيسية")
    page = st.radio(
        "",
        ["🏠 الرئيسية", "📦 المنتجات", "⚖️ مقارنة الأسعار", "🏆 أفضل العروض", "📈 تاريخ الأسعار", "📊 الرسوم البيانية"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    if st.button("🔄 تحديث البيانات الآن", use_container_width=True):
        run_update()

    st.markdown("---")

    if not df.empty and "timestamp" in df.columns:
        last_update = df["timestamp"].max() if "timestamp" in df.columns else "—"
        st.caption(f"آخر تحديث: {last_update}")

    store_count = df["store"].nunique() if not df.empty else 0
    st.caption(f"عدد المتاجر: {store_count}")
    scheduler_ok = st.session_state.get("scheduler_started", False)
    st.caption(f"الجدول اليومي: {'✅ يعمل' if scheduler_ok else '⚠️ متوقف'}")


# ===============================================================
# صفحة الرئيسية
# ===============================================================
if page == "🏠 الرئيسية":
    st.markdown("""
    <div class="main-header">
        <h1>⚡ مقارنة الأسعار الكهربائية — الكويت</h1>
        <p>منصة ذكية لمتابعة ومقارنة أسعار المتاجر الكهربائية الكويتية يومياً</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{len(df):,}</div>
            <div class="kpi-label">إجمالي المنتجات</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{df["store"].nunique() if not df.empty else 0}</div>
            <div class="kpi-label">عدد المتاجر</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{len(groups)}</div>
            <div class="kpi-label">منتجات مطابقة عبر المتاجر</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        avg_saving = round(sum(g.get("savings_pct", 0) for g in groups) / len(groups), 1) if groups else 0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{avg_saving}%</div>
            <div class="kpi-label">متوسط نسبة التوفير</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # أفضل 5 عروض
    if groups:
        st.markdown('<div class="section-title">🏆 أبرز العروض اليوم</div>', unsafe_allow_html=True)
        top5 = sorted(groups, key=lambda g: g.get("savings_pct", 0), reverse=True)[:5]
        for g in top5:
            st.markdown(f"""
            <div class="best-deal-card">
                <strong>{g['canonical_name']}</strong><br>
                أفضل سعر: <strong>{g['best_price']} KD</strong> — {g['best_store']} &nbsp;
                <span class="saving-badge">توفير {g['savings_pct']}%</span>
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
    st.title("📦 قائمة المنتجات")

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
        col_labels = {"name": "اسم المنتج", "price": "السعر (KD)", "store": "المتجر", "url": "رابط", "timestamp": "وقت الجلب"}
        show_df = filtered[display_cols].rename(columns=col_labels)
        st.dataframe(show_df, use_container_width=True, hide_index=True)


# ===============================================================
# صفحة مقارنة الأسعار
# ===============================================================
elif page == "⚖️ مقارنة الأسعار":
    st.title("⚖️ مقارنة الأسعار بين المتاجر")

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
            with st.expander(f"📦 {g['canonical_name']} — أفضل سعر: {g['best_price']} KD ({g['best_store']}) | توفير {g['savings_pct']}%"):
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
    st.title("🏆 أفضل العروض — أكبر فرق سعري بين المتاجر")

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

            # رسم بياني لأفضل 20 عرض
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
# صفحة تاريخ الأسعار
# ===============================================================
elif page == "📈 تاريخ الأسعار":
    st.title("📈 تاريخ الأسعار")

    if history_df.empty:
        st.warning("لا توجد بيانات تاريخية بعد. سيتم تجميعها تلقائياً عند كل تحديث.")
    else:
        product_names = sorted(history_df["name"].unique().tolist())
        selected_product = st.selectbox("اختر منتجاً لعرض تاريخ سعره:", product_names)

        if selected_product:
            product_history = history_df[history_df["name"] == selected_product].copy()
            product_history = product_history.sort_values("timestamp")

            stores_in_product = product_history["store"].unique().tolist()

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
    st.title("📊 الرسوم البيانية")

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
