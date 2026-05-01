from fastapi import FastAPI, Query
from scraper_aljassar import scrape_aljassar
from scraper_alarabiya import scrape_alarabiya
from scraper_xcite import scrape_xcite
from products_db import init_products_db, get_product_links
from database import insert_price, init_db

app = FastAPI()

init_db()
init_products_db()

@app.get("/price")
def get_price(product: str = Query(...)):
    links = get_product_links(product)

    if not links:
        return {"error": "المنتج غير موجود في قاعدة البيانات"}

    results = {}

    for store, url in links:
        if store == "aljassar":
            price = scrape_aljassar(url)
        elif store == "alarabiya":
            price = scrape_alarabiya(url)
        elif store == "xcite":
            price = scrape_xcite(url)
        else:
            price = None

        if price:
            insert_price(url, store, price)

        results[store] = price or "غير متوفر"

    return {
        "product": product,
        "prices": results
    }
