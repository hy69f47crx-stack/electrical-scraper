import json
import os
import re
from datetime import datetime

from dotenv import load_dotenv
import anthropic

load_dotenv()

PRODUCTS_FILE = "products_all.json"
WORK_DESCRIPTIONS_FILE = "work_descriptions.json"

SYSTEM_PROMPT = """أنت خبير في توصيف أعمال الكهرباء والمشتريات الكهربائية في الكويت.

مهمتك: تحليل قائمة المنتجات الكهربائية المجلوبة من المتاجر الكويتية (دخيل الجسار، العربية للكهرباء، اكسايت الغانم، يوبي) وتحويلها إلى بنود توصيف أعمال كهربائية واضحة ومفصّلة مع أسعارها بالدينار الكويتي.

فئات أعمال الكهرباء:
1. تمديدات وأسلاك كهربائية
2. لوحات التوزيع الكهربائية والقواطع
3. وحدات الإضاءة والتجهيزات
4. أجهزة التكييف والتبريد
5. مفاتيح وبرايز ووصلات
6. أجهزة الحماية والسيفتي
7. كابلات وقنوات كهربائية
8. أجهزة كهربائية منزلية
9. معدات ومواد كهربائية عامة

قواعد التوصيف:
- اكتب كل بند بصيغة "توريد وتركيب [اسم المنتج]، [المواصفات]"
- اذكر الوحدة المناسبة (قطعة، متر، مجموعة، نقطة)
- احسب السعر الأدنى والمتوسط والأقصى بناءً على الأسعار المتاحة
- اذكر المتجر الأفضل سعراً
- صنّف كل بند تحت فئته الصحيحة

أعد JSON نقي فقط بدون أي نص قبله أو بعده، بالشكل:
{"work_items": [...]}"""


def load_products() -> list:
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def chunk_products(products: list, chunk_size: int = 25) -> list[list]:
    return [products[i : i + chunk_size] for i in range(0, len(products), chunk_size)]


def build_products_text(products: list) -> str:
    lines = []
    for p in products:
        line = f"- {p.get('name', '')} | السعر: {p.get('price', '')} KD | المتجر: {p.get('store', '')}"
        lines.append(line)
    return "\n".join(lines)


def call_claude_for_chunk(client: anthropic.Anthropic, products_text: str, chunk_index: int) -> dict | None:
    user_message = f"""حلّل هذه المنتجات الكهربائية وحوّلها إلى بنود توصيف أعمال. أعد JSON نقي فقط:

{products_text}

الشكل المطلوب:
{{"work_items": [{{"item_no": 1, "description": "توريد وتركيب ...", "unit": "قطعة", "min_price": 0.0, "avg_price": 0.0, "max_price": 0.0, "best_store": "اسم المتجر", "category": "فئة العمل", "related_products": ["منتج"]}}]}}"""

    print(f"\n[AI] معالجة الدفعة {chunk_index + 1} ({len(products_text.splitlines())} منتج) ...")
    full_text = ""

    try:
        with client.messages.stream(
            model="claude-opus-4-7",
            max_tokens=16000,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            for text in stream.text_stream:
                full_text += text
                print(text, end="", flush=True)
        print()

        # استخراج JSON من الرد
        json_match = re.search(r'\{[\s\S]*"work_items"[\s\S]*\}', full_text)
        if json_match:
            return json.loads(json_match.group())

        print(f"[AI] لم يُعثر على JSON في رد الدفعة {chunk_index + 1}")
    except anthropic.APIError as e:
        print(f"[AI] خطأ في API: {e}")
    except json.JSONDecodeError as e:
        print(f"[AI] خطأ في تحليل JSON: {e}")
        print(f"[AI] آخر 200 حرف: {full_text[-200:]}")

    return None


def merge_work_items(chunks_results: list[dict], products_count: int) -> dict:
    all_items = []
    categories_summary: dict[str, int] = {}

    item_counter = 1
    for chunk in chunks_results:
        if not chunk:
            continue
        for item in chunk.get("work_items", []):
            item["item_no"] = item_counter
            all_items.append(item)
            cat = item.get("category", "عام")
            categories_summary[cat] = categories_summary.get(cat, 0) + 1
            item_counter += 1

    return {
        "work_items": all_items,
        "categories_summary": categories_summary,
        "total_work_items": len(all_items),
        "generated_at": datetime.now().isoformat(),
        "products_analyzed": products_count,
    }


def run_ai_agent() -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key or api_key == "PUT_YOUR_KEY_HERE":
        print("[AI] تحذير: ANTHROPIC_API_KEY غير محدد. أضفه في ملف .env")
        return {}

    products = load_products()
    if not products:
        print("[AI] لا توجد منتجات للتحليل. شغّل السكريبر أولاً.")
        return {}

    print(f"[AI] تحليل {len(products)} منتج بواسطة Claude ...")

    client = anthropic.Anthropic(api_key=api_key)
    chunks = chunk_products(products, chunk_size=25)
    print(f"[AI] تقسيم المنتجات إلى {len(chunks)} دفعة (25 منتج لكل دفعة)")
    results = []

    for i, chunk in enumerate(chunks):
        text = build_products_text(chunk)
        result = call_claude_for_chunk(client, text, i)
        if result:
            results.append(result)
            print(f"[AI] ✅ الدفعة {i+1}: {len(result.get('work_items', []))} بند")
        else:
            print(f"[AI] ⚠️ الدفعة {i+1}: فشلت")

    final = merge_work_items(results, len(products))

    with open(WORK_DESCRIPTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=4)

    print(f"\n[AI] ✅ تم حفظ {final['total_work_items']} بند توصيف في {WORK_DESCRIPTIONS_FILE}")
    return final


if __name__ == "__main__":
    run_ai_agent()
