from playwright.sync_api import sync_playwright
import json
import re
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PRODUCTS_FILE = BASE_DIR / "products_all.json"
HISTORY_FILE = BASE_DIR / "price_history.json"


def parse_price(raw: str) -> float | None:
    """يحوّل نص السعر إلى رقم (يزيل KD، د.ك، فواصل ...)."""
    if not raw:
        return None
    cleaned = re.sub(r"[^\d\.,]", "", raw.replace(",", "."))
    # احتفظ بأول رقم عشري صحيح
    match = re.search(r"\d+(?:\.\d+)?", cleaned)
    if match:
        return float(match.group())
    return None


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# 1) سكريبر الجسار
# ============================================================
def scrape_jassar(page) -> list:
    results = []
    base_url = "https://online.aljassar.com/shop/page/{}/"
    page_number = 1

    while True:
        url = base_url.format(page_number)
        print(f"[دخيل الجسار] الصفحة {page_number} ...")
        try:
            page.goto(url, timeout=40000, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            print(f"[دخيل الجسار] فشل تحميل الصفحة {page_number}: {e}")
            break
        time.sleep(3)

        # debug: اطبع عنوان الصفحة وعدد العناصر لمعرفة الـ selectors
        if page_number == 1:
            print(f"[دخيل الجسار][DEBUG] عنوان الصفحة: {page.title()}")
            print(f"[دخيل الجسار][DEBUG] URL الفعلي: {page.url}")
            for sel in ["li.product", "article.product", ".product", ".product-item",
                        ".product-card", "[class*='product']", ".wc-block-grid__product"]:
                count = page.locator(sel).count()
                if count:
                    print(f"[دخيل الجسار][DEBUG] selector '{sel}' → {count} عنصر")

        # جرّب selectors متعددة لـ WooCommerce
        for sel in ["li.product", "article.product", ".wc-block-grid__product",
                    ".product-card", ".product-item", ".products > li"]:
            products = page.locator(sel).all()
            if products:
                print(f"[دخيل الجسار] استخدم selector: {sel}")
                break

        if not products:
            print(f"[دخيل الجسار] انتهت الصفحات عند {page_number - 1}.")
            break

        for product in products:
            try:
                name = (
                    product.locator(".woocommerce-loop-product__title").first.text_content()
                    or product.locator("h2").first.text_content()
                    or product.locator("h3").first.text_content()
                )
                name = name.strip() if name else ""

                raw_price = product.locator(".price").first.text_content().strip()
                price = parse_price(raw_price)
                link_el = product.locator("a").first
                link = link_el.get_attribute("href") if link_el else ""

                if name and price is not None:
                    results.append({
                        "store": "دخيل الجسار",
                        "name": name,
                        "price": price,
                        "url": link or "",
                        "timestamp": now_str(),
                        "currency": "KD",
                    })
            except Exception:
                pass

        page_number += 1

    print(f"[دخيل الجسار] تم جلب {len(results)} منتج.")
    return results


# ============================================================
# 2) سكريبر العربية للكهرباء
# ============================================================
def scrape_arabian(page) -> list:
    results = []
    # جرّب URL بديل — الدومين الأصلي لا يُحلّ DNS
    candidates = [
        "https://arabianelectrical.com/shop/page/{}/",
        "https://www.arabian-electric.com/shop/page/{}/",
    ]
    base_url = None

    for candidate in candidates:
        try:
            page.goto(candidate.format(1), timeout=15000, wait_until="domcontentloaded")
            if "arabian" in page.url.lower() or "electric" in page.url.lower():
                base_url = candidate
                print(f"[العربية للكهرباء] URL يعمل: {candidate}")
                break
        except Exception:
            pass

    if not base_url:
        print("[العربية للكهرباء] ⚠️ الموقع غير متاح حالياً — تجاوز.")
        return []

    page_number = 2  # الصفحة 1 حُمّلت بالفعل
    while True:
        if page_number > 1:
            url = base_url.format(page_number)
            print(f"[العربية للكهرباء] الصفحة {page_number} ...")
            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
            except Exception as e:
                print(f"[العربية للكهرباء] فشل: {e}")
                break
            time.sleep(2)

        products = page.locator("li.product, article.product, .product").all()
        if not products:
            break

        for product in products:
            try:
                name = product.locator("h2, .woocommerce-loop-product__title").first.text_content().strip()
                raw_price = product.locator(".price").first.text_content().strip()
                price = parse_price(raw_price)
                link_el = product.locator("a").first
                link = link_el.get_attribute("href") if link_el else ""
                if name and price is not None:
                    results.append({
                        "store": "العربية للكهرباء",
                        "name": name,
                        "price": price,
                        "url": link or "",
                        "timestamp": now_str(),
                        "currency": "KD",
                    })
            except Exception:
                pass

        page_number += 1

    print(f"[العربية للكهرباء] تم جلب {len(results)} منتج.")
    return results


# ============================================================
# 3) سكريبر Extra Kuwait
# ============================================================
def scrape_extra(page) -> list:
    results = []
    # جرّب روابط متعددة لـ Extra Kuwait
    candidates = [
        "https://www.extra.com.kw/ar/category/electronics?start={}&sz=48",
        "https://www.extra.com/ar-kw/c/electronics/?start={}&sz=48",
        "https://www.extra.com/en-kw/c/electronics/?start={}&sz=48",
    ]
    base_url = None

    for candidate in candidates:
        try:
            page.goto(candidate.format(0), timeout=20000, wait_until="domcontentloaded")
            current = page.url
            if "extra.com" in current and "chrome-error" not in current and "ar-sa" not in current:
                base_url = candidate
                print(f"[Extra] URL يعمل: {candidate}")
                break
        except Exception:
            pass

    if not base_url:
        print("[Extra] ⚠️ الموقع غير متاح أو محجوب — تجاوز.")
        return []

    offset = 48  # الصفحة 0 حُمّلت بالفعل
    while True:
        if offset > 0:
            url = base_url.format(offset)
            print(f"[Extra] الصفحة offset={offset} ...")
            try:
                page.goto(url, timeout=40000)
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception as e:
                print(f"[Extra] فشل التحميل offset={offset}: {e}")
                break
            time.sleep(3)

        products = page.locator(".product-tile").all()
        if not products:
            print("[Extra] لا توجد منتجات إضافية.")
            break

        for product in products:
            try:
                name = product.locator(".product-name").text_content().strip()
                raw_price = product.locator(".price-value, .sales .value").first.text_content().strip()
                price = parse_price(raw_price)
                link_el = product.locator("a").first
                link = link_el.get_attribute("href") if link_el else ""

                if name and price is not None:
                    results.append({
                        "store": "Extra",
                        "name": name,
                        "price": price,
                        "url": ("https://www.extra.com" + link) if link and link.startswith("/") else (link or ""),
                        "timestamp": now_str(),
                        "currency": "KD",
                    })
            except Exception:
                pass

        offset += 48

        # توقف إذا تجاوزنا 10 صفحات (480 منتج)
        if offset > 480:
            break

    print(f"[Extra] تم جلب {len(results)} منتج.")
    return results


# ============================================================
# 4) سكريبر Xcite by Alghanim
# ============================================================
def scrape_xcite(page) -> list:
    results = []
    # xcite.com أصبح يعيد توجيه إلى extra.com — جرّب xcite.com.kw
    base_url = "https://www.xcite.com.kw/en/electronics?p={}"
    page_number = 1

    while True:
        url = base_url.format(page_number)
        print(f"[اكسايت الغانم] الصفحة {page_number} ...")
        try:
            page.goto(url, timeout=40000, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception as e:
            print(f"[اكسايت الغانم] فشل التحميل الصفحة {page_number}: {e}")
            break

        # تحقق إننا لم نُعاد توجيهنا خارج xcite
        if "xcite" not in page.url.lower():
            print(f"[اكسايت الغانم] ⚠️ أُعيد التوجيه إلى {page.url} — تجاوز.")
            break

        time.sleep(3)

        products = page.locator(".product-item-info, [data-product-sku], .product-item").all()
        if not products:
            print("[اكسايت الغانم] لا توجد منتجات إضافية.")
            break

        for product in products:
            try:
                name = product.locator(".product-item-name, .product-name").text_content().strip()
                raw_price = product.locator(".price").first.text_content().strip()
                price = parse_price(raw_price)
                link_el = product.locator("a").first
                link = link_el.get_attribute("href") if link_el else ""

                if name and price is not None:
                    results.append({
                        "store": "اكسايت الغانم",
                        "name": name,
                        "price": price,
                        "url": link or "",
                        "timestamp": now_str(),
                        "currency": "KD",
                    })
            except Exception:
                pass

        page_number += 1

        # توقف بعد 10 صفحات
        if page_number > 10:
            break

    print(f"[اكسايت الغانم] تم جلب {len(results)} منتج.")
    return results


# ============================================================
# 5) سكريبر يوبي للكهرباء
# ============================================================
def scrape_youbi(page) -> list:
    results = []
    # ubay.com.kw لا يُحلّ DNS — جرّب ubay.com
    base_url = "https://www.ubay.com/shop/page/{}/"
    page_number = 1

    while True:
        url = base_url.format(page_number)
        print(f"[يوبي] الصفحة {page_number} ...")
        try:
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            print(f"[يوبي] فشل تحميل الصفحة {page_number}: {e}")
            break
        time.sleep(2)

        products = page.locator(".product, .product-item, li.product").all()
        if not products:
            print("[يوبي] لا توجد صفحات إضافية.")
            break

        for product in products:
            try:
                name = product.locator("h2, .woocommerce-loop-product__title, .product-name").first.text_content().strip()
                raw_price = product.locator(".price, .woocommerce-Price-amount").first.text_content().strip()
                price = parse_price(raw_price)
                link_el = product.locator("a").first
                link = link_el.get_attribute("href") if link_el else ""

                if name and price is not None:
                    results.append({
                        "store": "يوبي",
                        "name": name,
                        "price": price,
                        "url": link or "",
                        "timestamp": now_str(),
                        "currency": "KD",
                    })
            except Exception:
                pass

        page_number += 1

        if page_number > 15:
            break

    print(f"[يوبي] تم جلب {len(results)} منتج.")
    return results


# ============================================================
# 6) تحديث السجل التاريخي للأسعار
# ============================================================
def update_price_history(new_products: list):
    """يضيف المنتجات الجديدة إلى سجل الأسعار التاريخي."""
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.extend(new_products)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

    print(f"[السجل] تم إضافة {len(new_products)} سجل تاريخي. الإجمالي: {len(history)}")


# ============================================================
# 7) السكريبر الشامل
# ============================================================
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def scrape_all():
    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=UA, locale="ar-KW")

        # دخيل الجسار
        all_results.extend(scrape_jassar(page))

        # العربية للكهرباء
        all_results.extend(scrape_arabian(page))

        # Extra Kuwait
        all_results.extend(scrape_extra(page))

        # اكسايت الغانم
        all_results.extend(scrape_xcite(page))

        # يوبي
        all_results.extend(scrape_youbi(page))

        browser.close()

    if not all_results:
        print("[السكريبر] ⚠️ لم يُجلب أي منتج — الملف القديم محفوظ كما هو.")
        return []

    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

    print(f"[السكريبر] تم حفظ {len(all_results)} منتج في {PRODUCTS_FILE}")

    update_price_history(all_results)

    return all_results


if __name__ == "__main__":
    scrape_all()
