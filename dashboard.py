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
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
}

.main-header {
    background: linear-gradient(135deg, #0d1b2a 0%, #1b4f72 50%, #0f3460 100%);
    padding: 28px 36px;
    border-radius: 18px;
    color: white;
    margin-bottom: 28px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.18);
}
.main-header h1 { font-size: 2.1rem; margin: 0; color: #ffffff; font-weight: 900; }
.main-header p  { font-size: 1.05rem; margin: 8px 0 0; color: #b2c6e0; }

.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 22px 16px;
    text-align: center;
    box-shadow: 0 2px 14px rgba(0,0,0,0.09);
    border-top: 4px solid #0f3460;
    transition: transform .15s;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-card .kpi-value { font-size: 2.1rem; font-weight: 900; color: #0f3460; }
.kpi-card .kpi-label { font-size: 0.88rem; color: #718096; margin-top: 6px; }

.best-deal-card {
    background: linear-gradient(135deg, #f0fff4, #c6f6d5);
    border-radius: 12px;
    padding: 16px 20px;
    border-right: 5px solid #38a169;
    margin-bottom: 10px;
    box-shadow: 0 1px 6px rgba(56,161,105,0.12);
}

.work-item-card {
    background: linear-gradient(135deg, #f0f4ff, #e8eeff);
    border-radius: 12px;
    padding: 16px 20px;
    border-right: 5px solid #4263eb;
    margin-bottom: 10px;
    box-shadow: 0 1px 6px rgba(66,99,235,0.10);
}
.work-item-card .item-desc { font-weight: 700; font-size: 1.02rem; color: #2d3748; }
.work-item-card .item-price { color: #276749; font-weight: 700; font-size: 1rem; }
.work-item-card .item-category {
    background: #4263eb;
    color: white;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.78rem;
    font-weight: 700;
}

.saving-badge {
    background: #38a169;
    color: white;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.82rem;
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

.ai-badge {
    background: linear-gradient(90deg, #6c5ce7, #a855f7);
    color: white;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.82rem;
    font-weight: 700;
}

.info-box {
    background: #ebf8ff;
    border-right: 4px solid #3182ce;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 12px;
    color: #2c5282;
    font-size: 0.92rem;
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
        return df.dropna(subset=["price"])
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


@st.cache_data(ttl=300)
def load_work_descriptions():
    try:
        with open("work_descriptions.json", "r", encoding="utf-8") as f:
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
    steps = ["scraper.py", "matcher.py"]
    if run_ai:
        steps.append("ai_agent.py")

    label = "جاري تحديث البيانات" + (" وتوليد توصيف الأعمال بالذكاء الاصطناعي" if run_ai else "")
    with st.spinner(f"{label} ... قد يستغرق هذا بضع دقائق"):
        try:
            for script in steps:
                subprocess.run(
                    [sys.executable, script],
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
                [sys.executable, "ai_agent.py"],
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
    st.markdown("## ⚡ القائمة الرئيسية")
    page = st.radio(
        "",
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

    st.markdown("---")

    if st.button("🔄 تحديث البيانات الآن", use_container_width=True):
        run_update(run_ai=False)

    if st.button("🤖 تحديث + توصيف الأعمال", use_container_width=True):
        run_update(run_ai=True)

    st.markdown("---")

    if not df.empty and "timestamp" in df.columns:
        last_ts = df["timestamp"].max()
        st.caption(f"آخر تحديث للمنتجات: {last_ts}")

    if work_data:
        gen_at = work_data.get("generated_at", "")
        if gen_at:
            try:
                gen_dt = datetime.fromisoformat(gen_at).strftime("%Y-%m-%d %H:%M")
            except ValueError:
                gen_dt = gen_at
            st.caption(f"آخر تحديث للتوصيف: {gen_dt}")

    store_count = df["store"].nunique() if not df.empty else 0
    st.caption(f"عدد المتاجر: {store_count}")
    scheduler_ok = st.session_state.get("scheduler_started", False)
    st.caption(f"الجدول اليومي: {'✅ يعمل' if scheduler_ok else '⚠️ متوقف'}")
    work_items_count = len(work_data.get("work_items", []))
    if work_items_count:
        st.caption(f"بنود التوصيف: {work_items_count}")


# ===============================================================
# صفحة الرئيسية
# ===============================================================
if page == "🏠 الرئيسية":
    st.markdown("""
    <div class="main-header">
        <h1>⚡ مقارنة الأسعار الكهربائية — الكويت</h1>
        <p>منصة ذكية لمتابعة ومقارنة أسعار المتاجر الكهربائية الكويتية مع توصيف أعمال بالذكاء الاصطناعي</p>
    </div>
    """, unsafe_allow_html=True)

    work_items_count = len(work_data.get("work_items", []))
    avg_saving = round(sum(g.get("savings_pct", 0) for g in groups) / len(groups), 1) if groups else 0

    col1, col2, col3, col4, col5 = st.columns(5)

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
            <div class="kpi-label">منتجات متطابقة عبر المتاجر</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{avg_saving}%</div>
            <div class="kpi-label">متوسط نسبة التوفير</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{work_items_count}</div>
            <div class="kpi-label">بنود توصيف الأعمال</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # أفضل العروض
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

    # أبرز بنود التوصيف
    if work_data.get("work_items"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">🤖 أبرز بنود توصيف الأعمال <span class="ai-badge">AI</span></div>', unsafe_allow_html=True)
        items_preview = work_data["work_items"][:5]
        for item in items_preview:
            st.markdown(f"""
            <div class="work-item-card">
                <span class="item-category">{item.get("category", "")}</span>
                <div class="item-desc">{item.get("description", "")}</div>
                <div class="item-price">
                    أدنى سعر: {item.get("min_price", "—")} KD &nbsp;|&nbsp;
                    متوسط: {item.get("avg_price", "—")} KD &nbsp;|&nbsp;
                    أعلى: {item.get("max_price", "—")} KD
                    &nbsp;— أفضل متجر: {item.get("best_store", "—")}
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
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
        <h1 style="margin:0;">🤖 توصيف الأعمال الكهربائية</h1>
        <span class="ai-badge">مدعوم بـ Claude AI</span>
    </div>
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
    st.title("📈 تاريخ الأسعار")

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
