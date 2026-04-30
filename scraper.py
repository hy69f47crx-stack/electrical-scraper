from playwright.sync_api import sync_playwright
import json
import re
import time
from datetime import datetime

PRODUCTS_FILE = "products_all.json"
HISTORY_FILE = "price_history.json"


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
        print(f"[الجسار] الصفحة {page_number} ...")
        try:
            page.goto(url, timeout=30000)
        except Exception as e:
            print(f"[الجسار] فشل تحميل الصفحة {page_number}: {e}")
            break
        time.sleep(2)

        products = page.locator(".product").all()
        if not products:
            print("[الجسار] لا توجد صفحات إضافية.")
            break

        for product in products:
            try:
                name = product.locator("h2").text_content().strip()
                raw_price = product.locator(".price").text_content().strip()
                price = parse_price(raw_price)
                link = product.locator("a").first.get_attribute("href")

                if name and price is not None:
                    results.append({
                        "store": "الجسار",
                        "name": name,
                        "price": price,
                        "url": link or "",
                        "timestamp": now_str(),
                        "currency": "KD",
                    })
            except Exception:
                pass

        page_number += 1

    print(f"[الجسار] تم جلب {len(results)} منتج.")
    return results


# ============================================================
# 2) سكريبر العربية للكهرباء
# ============================================================
def scrape_arabian(page) -> list:
    results = []
    base_url = "https://www.arabian-electrical.com/shop/page/{}/"
    page_number = 1

    while True:
        url = base_url.format(page_number)
        print(f"[العربية] الصفحة {page_number} ...")
        try:
            page.goto(url, timeout=30000)
        except Exception as e:
            print(f"[العربية] فشل تحميل الصفحة {page_number}: {e}")
            break
        time.sleep(2)

        products = page.locator(".product").all()
        if not products:
            print("[العربية] لا توجد صفحات إضافية.")
            break

        for product in products:
            try:
                name = product.locator("h2").text_content().strip()
                raw_price = product.locator(".price").text_content().strip()
                price = parse_price(raw_price)
                link = product.locator("a").first.get_attribute("href")

                if name and price is not None:
                    results.append({
                        "store": "العربية",
                        "name": name,
                        "price": price,
                        "url": link or "",
                        "timestamp": now_str(),
                        "currency": "KD",
                    })
            except Exception:
                pass

        page_number += 1

    print(f"[العربية] تم جلب {len(results)} منتج.")
    return results


# ============================================================
# 3) سكريبر Extra Kuwait
# ============================================================
def scrape_extra(page) -> list:
    results = []
    base_url = "https://www.extra.com/ar-kw/c/electronics/?start={}&sz=48"
    offset = 0

    while True:
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
    base_url = "https://www.xcite.com/electronics?p={}"
    page_number = 1

    while True:
        url = base_url.format(page_number)
        print(f"[Xcite] الصفحة {page_number} ...")
        try:
            page.goto(url, timeout=40000)
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception as e:
            print(f"[Xcite] فشل التحميل الصفحة {page_number}: {e}")
            break
        time.sleep(3)

        products = page.locator(".product-item-info, [data-product-sku]").all()
        if not products:
            print("[Xcite] لا توجد منتجات إضافية.")
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
                        "store": "Xcite",
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

    print(f"[Xcite] تم جلب {len(results)} منتج.")
    return results


# ============================================================
# 5) تحديث السجل التاريخي للأسعار
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
# 6) السكريبر الشامل
# ============================================================
def scrape_all():
    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # الجسار
        all_results.extend(scrape_jassar(page))

        # العربية
        all_results.extend(scrape_arabian(page))

        # Extra Kuwait
        all_results.extend(scrape_extra(page))

        # Xcite
        all_results.extend(scrape_xcite(page))

        browser.close()

    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

    print(f"[السكريبر] تم حفظ {len(all_results)} منتج في {PRODUCTS_FILE}")

    update_price_history(all_results)

    return all_results


if __name__ == "__main__":
    scrape_all()
