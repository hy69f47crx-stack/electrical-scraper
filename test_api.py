import requests

API_URL = "http://127.0.0.1:8000/price"
PRODUCT_URL = "https://online.aljassar.com/product/mcb-63a-1p-10ka"

response = requests.get(API_URL, params={"url": PRODUCT_URL})
print(response.json())
