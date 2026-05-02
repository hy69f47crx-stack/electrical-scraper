# مشروع مقارنة الأسعار الكهربائية - ملخص الكود

## الملفات الرئيسية:

### 1. dashboard.py
الملف الرئيسي - يحتوي على واجهة Streamlit كاملة مع:
- 8 صفحات: الرئيسية، المنتجات، الفئات، المقارنة، أفضل العروض، التوصيفات، تاريخ الأسعار، الرسوم البيانية
- Dark theme مع colors RTL-compatible
- KPI cards responsive
- جداول مع horizontal scroll
- Altair charts مع RTL support
- Sidebar toggle button
- Update menu (⚙️ popover)

### 2. scraper.py
سكريبر الويب - يجلب بيانات من 5 متاجر:
- دخيل الجسار (Al-Jassar)
- العربية للكهرباء (Arabian Electrical)
- Extra Kuwait
- Xcite by Alghanim
- يوبي (Ubay)

المخرجات:
- `products_all.json` - قائمة المنتجات الحالية
- `price_history.json` - السجل التاريخي للأسعار

### 3. matcher.py
عميل ذكي لمطابقة المنتجات:
- تطبيع النصوص العربية/الإنجليزية
- مطابقة fuzzy مع threshold 75%
- استخراج رقم الموديل للمطابقة الأدق
- المخرج: `matched_groups.json`

### 4. ai_agent.py
عميل Claude AI لتوليد توصيفات الأعمال:
- استقراء توصيفات كهربائية احترافية
- حساب نطاقات الأسعار
- المخرج: `work_descriptions.json`

### 5. scheduler.py
جدولة التحديثات اليومية:
- يعمل الساعة 2 صباحاً بتوقيت الكويت
- ينفذ: scraper → matcher → ai_agent
- يعمل في الخلفية (background scheduler)

## ملفات البيانات:

```
products_all.json
├─ name: string
├─ price: float (KD)
├─ store: string
├─ url: string
├─ timestamp: datetime
└─ currency: "KD"

matched_groups.json
├─ group_id: uuid
├─ canonical_name: string
├─ products: array
├─ best_store: string
├─ best_price: float
├─ worst_price: float
├─ savings_pct: int
└─ last_updated: date

price_history.json
├─ name: string
├─ price: float
├─ store: string
└─ timestamp: datetime

work_descriptions.json
├─ work_items: array
│  ├─ item_no: int
│  ├─ description: string
│  ├─ category: string
│  ├─ unit: string
│  ├─ min_price: float
│  ├─ avg_price: float
│  ├─ max_price: float
│  └─ best_store: string
├─ categories_summary: object
├─ total_work_items: int
└─ products_analyzed: int
```

## التغييرات الأخيرة (2024-05-02):

### إصلاحات RTL و Responsive:
1. ✅ RTL support كامل لـ Altair charts (Cairo font)
2. ✅ @media queries للـ mobile (480px) و tablet (768px)
3. ✅ KPI cards responsive
4. ✅ st.table() → st.dataframe() (horizontal scroll)
5. ✅ Expander headers truncation (35 char max)
6. ✅ Store grid responsive (1/2/3 columns)
7. ✅ CSS balanced padding/margins

### إصلاحات الواجهة:
1. ✅ Hide collapse button و expand more
2. ✅ Sidebar toggle button (☰)
3. ✅ Remove deals section
4. ✅ Add categories page
5. ✅ Dark theme complete redesign

## كيفية الاستخدام:

```bash
# 1. ثبت المكتبات
pip install -r requirements.txt

# 2. أضف API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 3. شغّل السكريبر مباشرة (اختياري)
python scraper.py
python matcher.py

# 4. شغّل الداشبورد
streamlit run dashboard.py
```

## المتطلبات (requirements.txt):

```
streamlit>=1.28
pandas>=2.0
altair>=5.0
playwright>=1.40
rapidfuzz>=3.0
anthropic>=0.25
apscheduler>=3.10
pytz>=2024.1
pyarrow>=14.0
python-dotenv>=1.0
```

## الميزات الرئيسية:

✅ مقارنة أسعار 5 متاجر كويتية
✅ عميل AI لتوليد توصيفات
✅ تحديث يومي تلقائي
✅ واجهة عربية RTL كاملة
✅ Dark theme حديث
✅ Responsive design (mobile/tablet/desktop)
✅ جداول مع horizontal scroll
✅ رسوم بيانية تفاعلية
✅ بحث وفلترة متقدمة
✅ تتبع تاريخ الأسعار

## الأداء:

- ⚡ تحميل البيانات: < 1 ثانية
- 📊 تحديث المطابقة: < 5 ثواني
- 🤖 توليد التوصيفات: 30-60 ثانية
- 🔄 تحديث كامل: < 2 دقيقة
