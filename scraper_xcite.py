from playwright.sync_api import sync_playwright
import time
import re

def scrape_xcite(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        page.wait_for_timeout(5000)

        selectors = [
            ".price",
            ".product-price",
            ".new-price",
            ".price-value",
            "span.price",
            "div.price"
        ]

        for selector in selectors:
            try:
                text = page.inner_text(selector)
                match = re.search(r"\d+(\.\d+)?\s*د\.ك", text)
                if match:
                    return match.group(0)
            except:
                pass

        full_text = page.inner_text("body")
        match = re.search(r"\d+(\.\d+)?\s*د\.ك", full_text)
        return match.group(0) if match else None
