import sqlite3
import os

DB_PATH = "data/listings.db"

def build_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rental_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_number TEXT NOT NULL,
            suburb TEXT,
            city TEXT,
            munis TEXT,
            property_type TEXT,
            bedrooms REAL,
            bathrooms REAL,
            parking REAL,
            floor_size REAL,
            price REAL,
            has_security BOOLEAN,
            is_modern BOOLEAN,
            is_estate BOOLEAN,
            scraped_at TIMESTAMP NOT NULL,
            UNIQUE(listing_number, scraped_at)
        )
    """)

    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rental_listing ON rental_history(listing_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rental_scraped ON rental_history(scraped_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rental_suburb ON rental_history(suburb)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rental_munis ON rental_history(munis)")

    # Sales table (static)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            listing_number TEXT PRIMARY KEY,
            suburb TEXT,
            city TEXT,
            munis TEXT,
            property_type TEXT,
            bedrooms REAL,
            bathrooms REAL,
            parking REAL,
            floor_size REAL,
            price REAL,
            has_security BOOLEAN,
            is_modern BOOLEAN,
            is_estate BOOLEAN,
            scraped_at TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")

if __name__ == "__main__":
    build_database()