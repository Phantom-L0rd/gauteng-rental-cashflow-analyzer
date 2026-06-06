import pandas as pd
import sqlite3
from datetime import datetime

DB_PATH = "data/listings.db"
PARQUET_PATH = "data/2_silver_cleaned/type=rent/listings.parquet"

def migrate_rentals():
    print(f"Starting migration for rentals at {datetime.now()}")
    df = pd.read_parquet(PARQUET_PATH)
    
    df = df[df['price'] >= 2000]
    df = df[df['price'] <= 80000]
    df = df[df['bedrooms'].between(0, 8)]
    df = df[df['floor_size'] >= 15]
    df = df[df['floor_size'] <= 1500] 
    df = df[df['price_sqm'].between(30, 800)]

    df = df[['listing_number', 'scrape_at', 'price', 'type', 'suburb',
       'city', 'munis', 'bedrooms', 'bathrooms', 'parking', 'floor_size',
       'is_estate', 'has_security', 'is_modern']]
    
    df = df.rename(columns={
        'type': 'property_type',
        'scrape_at': 'scraped_at'
    })

    conn = sqlite3.connect(DB_PATH)

    df.to_sql('rental_history', conn, if_exists='append', index=False)
    conn.close()
    print(f"Migrated {len(df)} rows to rental_history")

if __name__ == "__main__":
    migrate_rentals()