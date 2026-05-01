import sqlite3

def init_db():
    conn = sqlite3.connect("prices.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_url TEXT,
            store TEXT,
            price TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def insert_price(product_url, store, price):
    conn = sqlite3.connect("prices.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO prices (product_url, store, price)
        VALUES (?, ?, ?)
    """, (product_url, store, price))

    conn.commit()
    conn.close()
