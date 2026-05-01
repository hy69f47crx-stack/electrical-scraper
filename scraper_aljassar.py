from playwright.sync_api import sync_playwright
import re
import time

def scrape_aljassar(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        time.sleep(5)

        full_text = page.inner_text("body")

        match = re.search(r"\d+(\.\d+)?\s*د\.ك", full_text)
        return match.group(0) if match else None
