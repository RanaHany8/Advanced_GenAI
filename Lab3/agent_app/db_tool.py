import sqlite3
from langchain.tools import tool

conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER
)
""")

cursor.execute("SELECT COUNT(*) FROM products")
count = cursor.fetchone()[0]

if count == 0:
    cursor.execute("INSERT INTO products (name, price) VALUES ('Laptop', 1000)")
    cursor.execute("INSERT INTO products (name, price) VALUES ('Phone', 500)")
    conn.commit()


@tool
def search_products(query: str) -> str:
    """
    Search for products in the database using a keyword.
    Returns a list of matching products with their prices.
    """
    cursor.execute(
        "SELECT name, price FROM products WHERE name LIKE ?",
        ('%' + query + '%',)
    )
    
    results = cursor.fetchall()

    if not results:
        return "No products found."

    return "\n".join([f"{name} - ${price}" for name, price in results])