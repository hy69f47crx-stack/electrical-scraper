import json
import re
import uuid
from datetime import date
from rapidfuzz import fuzz

PRODUCTS_FILE = "products_all.json"
MATCHED_FILE = "matched_groups.json"

SIMILARITY_THRESHOLD = 75


def normalize_text(text: str) -> str:
    """تطبيع النص العربي والإنجليزي لأغراض المقارنة."""
    text = text.lower()
    # توحيد أشكال الألف والهمزة
    text = re.sub(r"[أإآ]", "ا", text)
    # حذف التشكيل
    text = re.sub(r"[ً-ٟ]", "", text)
    # توحيد التاء المربوطة
    text = text.replace("ة", "ه")
    # حذف الرموز غير الضرورية
    text = re.sub(r"[^\w\s]", " ", text)
    # تقليص المسافات
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_model_tokens(name: str) -> set:
    """استخراج أرقام الموديل والبراندات من اسم المنتج."""
    # أرقام وحروف مثل LG55UN7300، SAMSUNG، WM1000 ...
    tokens = re.findall(r"[A-Z]{2,}[\w]*|[A-Z0-9]{3,}", name.upper())
    return set(tokens)


def similarity_score(name_a: str, name_b: str) -> float:
    """يحسب درجة التشابه بين اسمين مع مكافأة تطابق رموز الموديل."""
    norm_a = normalize_text(name_a)
    norm_b = normalize_text(name_b)

    base_score = fuzz.token_sort_ratio(norm_a, norm_b)

    # مكافأة 10 نقاط إذا تشارك الاسمان رمز موديل مشترك
    tokens_a = extract_model_tokens(name_a)
    tokens_b = extract_model_tokens(name_b)
    if tokens_a and tokens_b and tokens_a & tokens_b:
        base_score = min(100, base_score + 10)

    return base_score


def match_products(all_products: list) -> list:
    """
    يطابق المنتجات المتشابهة عبر المتاجر المختلفة.
    يعيد قائمة من المجموعات، كل مجموعة تضم نفس المنتج من متاجر متعددة.
    """
    matched_indices = set()
    groups = []

    for i, product_a in enumerate(all_products):
        if i in matched_indices:
            continue

        group = [product_a]
        matched_indices.add(i)

        for j in range(i + 1, len(all_products)):
            if j in matched_indices:
                continue
            product_b = all_products[j]

            # لا نطابق منتجات من نفس المتجر
            if product_a["store"] == product_b["store"]:
                continue

            score = similarity_score(product_a["name"], product_b["name"])
            if score >= SIMILARITY_THRESHOLD:
                group.append(product_b)
                matched_indices.add(j)

        # نحتفظ فقط بالمجموعات التي تضم منتجات من أكثر من متجر واحد
        if len(group) > 1:
            groups.append(group)

    return groups


def build_comparison_groups() -> list:
    """
    يقرأ products_all.json ويبني مجموعات المقارنة ويحفظها في matched_groups.json.
    """
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            all_products = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_products = []

    if not all_products:
        print("[المطابق] لا توجد منتجات للمعالجة.")
        with open(MATCHED_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return []

    print(f"[المطابق] معالجة {len(all_products)} منتج ...")
    groups = match_products(all_products)
    print(f"[المطابق] تم إيجاد {len(groups)} مجموعة متطابقة.")

    result = []
    today = str(date.today())

    for group in groups:
        prices = [p["price"] for p in group if isinstance(p.get("price"), (int, float))]
        if not prices:
            continue

        best_price = min(prices)
        worst_price = max(prices)
        best_item = next(p for p in group if p.get("price") == best_price)
        savings_pct = round((worst_price - best_price) / worst_price * 100, 1) if worst_price > 0 else 0

        result.append({
            "group_id": str(uuid.uuid4()),
            "canonical_name": best_item["name"],
            "products": [
                {
                    "store": p.get("store", ""),
                    "name": p.get("name", ""),
                    "price": p.get("price"),
                    "url": p.get("url", ""),
                }
                for p in group
            ],
            "best_store": best_item.get("store", ""),
            "best_price": best_price,
            "worst_price": worst_price,
            "savings_pct": savings_pct,
            "last_updated": today,
        })

    with open(MATCHED_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"[المطابق] تم حفظ المجموعات في {MATCHED_FILE}")
    return result


if __name__ == "__main__":
    build_comparison_groups()
