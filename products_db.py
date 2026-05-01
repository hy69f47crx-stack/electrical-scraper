
import sqlite3

def init_products_db():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            store TEXT,
            url TEXT
        )
    """)

    conn.commit()
    conn.close()

def add_product(name, store, url):
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (name, store, url)
        VALUES (?, ?, ?)
    """, (name, store, url))

    conn.commit()
    conn.close()

def get_product_links(name):
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT store, url FROM products WHERE name = ?
    """, (name,))

    rows = cursor.fetchall()
    conn.close()
    return rows
