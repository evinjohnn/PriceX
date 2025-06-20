import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                asin VARCHAR(255) UNIQUE NOT NULL,
                title TEXT,
                url TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS price_history (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                price DECIMAL(10,2),
                stock_status VARCHAR(50),
                image_url TEXT, -- Added image_url
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))
        print("Database initialized.")
        conn.commit()

def add_product_if_not_exists(asin, title, url):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id FROM products WHERE asin = :asin"), {"asin": asin}).fetchone()
        if result:
            return result[0]
        else:
            insert_result = conn.execute(text("""
                INSERT INTO products (asin, title, url) VALUES (:asin, :title, :url) RETURNING id
            """), {"asin": asin, "title": title, "url": url}).fetchone()
            conn.commit()
            return insert_result[0]

def add_price_entry(product_id, price, stock_status, image_url):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO price_history (product_id, price, stock_status, image_url) 
            VALUES (:product_id, :price, :stock_status, :image_url)
        """), {"product_id": product_id, "price": price, "stock_status": stock_status, "image_url": image_url})
        conn.commit()

def get_results_by_query(query: str):
    results = {"amazon": [], "flipkart": []}
    with engine.connect() as conn:
        db_query = text("""
            WITH LatestEntries AS (
                SELECT 
                    product_id,
                    price,
                    image_url,
                    ROW_NUMBER() OVER(PARTITION BY product_id ORDER BY timestamp DESC) as rn
                FROM price_history
            )
            SELECT
                p.title as name,
                le.price,
                p.url,
                le.image_url as image
            FROM products p
            JOIN LatestEntries le ON p.id = le.product_id AND le.rn = 1
            WHERE p.title ILIKE :query;
        """)
        db_results = conn.execute(db_query, {"query": f"%{query}%"}).mappings().all()

        for row in db_results:
            platform = "amazon" if "amazon" in row['url'] else "flipkart"
            results[platform].append({
                "name": row['name'], "price": str(row['price']), "url": row['url'],
                "image": row['image'], "platform": platform, "rating": "N/A", "reviews": "N/A"
            })
    return results

if __name__ == '__main__':
    init_db()