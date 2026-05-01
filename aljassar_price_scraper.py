from playwright.sync_api import sync_playwright
import re
import time

URL = "https://online.aljassar.com/product/mcb-63a-1p-10ka"

def get_price():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL)

        # ننتظر تحميل الصفحة
        time.sleep(5)

        # نقرأ كل النصوص
        full_text = page.inner_text("body")

        # نبحث عن السعر بصيغة عربية مثل: 1.75 د.ك
        match = re.search(r"\d+(\.\d+)?\s*د\.ك", full_text)
        if match:
            return match.group(0)

        return "ما لقيت السعر"

if __name__ == "__main__":
    price = get_price()
    print("السعر:", price)
