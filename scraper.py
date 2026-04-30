from playwright.sync_api import sync_playwright
import json
import time

# ============================
# 1) سكريبر الجسار
# ============================
def scrape_jassar(page):
    results = []
    base_url = "https://online.aljassar.com/shop/page/{}/"
    page_number = 1

    while True:
        url = base_url.format(page_number)
        print(f"[الجسار] قراءة الصفحة {page_number} ...")
        page.goto(url)
        time.sleep(2)

        products = page.locator(".product").all()
        if len(products) == 0:
            print("[الجسار] لا توجد صفحات إضافية.")
            break

        for product in products:
            try:
                name = product.locator("h2").text_content().strip()
                price = product.locator(".price").text_content().strip()
                link = product.locator("a").first.get_attribute("href")

                results.append({
                    "store": "الجسار",
                    "name": name,
                    "price": price,
                    "url": link
                })
            except:
                pass

        page_number += 1

    return results


# ============================
# 2) سكريبر العربية (موقع تحت الصيانة)
# ============================
def scrape_arabian(page):
    print("[العربية] الموقع تحت الصيانة — سيتم تفعيل السكريبر لاحقاً.")
    return []


# ============================
# 3) سكريبر شامل
# ============================
def scrape_all():
    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # الجسار
        all_results.extend(scrape_jassar(page))

        # العربية
        all_results.extend(scrape_arabian(page))

        browser.close()

    with open("products_all.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

    print("تم حفظ جميع منتجات الجسار والعربية في products_all.json")


# ============================
# 4) تشغيل السكريبر
# ============================
if __name__ == "__main__":
    scrape_all()
