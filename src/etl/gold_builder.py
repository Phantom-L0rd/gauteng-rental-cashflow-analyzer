"""
src/etl/gold_builder.py
Aggregates Silver data into Market Overview stats.
"""
import pandas as pd
import glob
import os
import logging

from src.utils.data_controller import load_parquet, save_parquet

class GoldAnalyticsBuilder:
    def __init__(self):
        self.silver_dir = "data/2_silver_cleaned"
        self.gold_dir = "data/3_gold_analytics"
        self.feat_dir = "data/4_feature_store"
        self.logger = logging.getLogger("GoldBuilder")

    def build_market_overview(self, rentals=True):
        listing_type = "rent" if rentals else "sale"
        self.logger.info(f"🏆 Creating Gold Market Overview for {listing_type}")

        # 1. Load all Silver Master files
        path = f"{self.silver_dir}/type={listing_type}/listings.parquet"

        df = load_parquet(path)

        df = df.sort_values('scrape_at', ascending=False).drop_duplicates('listing_number')

        # 2. Aggregation Logic
        # We group by Suburb and City to get high-level metrics
        overview = df.groupby(['munis', 'city', 'location']).agg(
            total_listings=('listing_number', 'count'),
            median_price=('price', 'median'),
            avg_price_per_m2=('price', lambda x: (x / df.loc[x.index, 'floor_size']).mean()),
        ).reset_index()

        # 4. Save to Gold
        os.makedirs(self.gold_dir, exist_ok=True)
        save_parquet(overview, self.gold_dir, f"market_overview_{listing_type}.parquet")
        
        self.logger.info(f"✅ Gold Table Saved: {len(overview)} suburbs summarized.")
    
    def build_rental_ratio(self):
        rentals_df = load_parquet(f'{self.silver_dir}/type=rent/listings.parquet')
        sales_df = load_parquet(f'{self.silver_dir}/type=sale/listings.parquet')

        rentals_count = rentals_df['location'].value_counts().reset_index()
        sales_count = sales_df['location'].value_counts().reset_index()

        df_counts = rentals_count.merge(sales_count,how='outer', on='location')
        df_counts = df_counts.fillna(0)
        df_counts.columns = ['location', 'count_rentals', 'count_sales']

        save_parquet(df_counts, self.feat_dir, 'market_count.parquet')
    
    def build_sales_yield(self):
        self.logger.info("🏆 Calculate Gross yield for sale properties ")
        
        df = load_parquet(f"{self.gold_dir}/sales/predicted_rent.parquet")
        
        if not os.path.exists(f"{self.feat_dir}/market_count.parquet"):
            self.build_rental_ratio()
        
        df_counts = load_parquet(f"{self.feat_dir}/market_count.parquet")

        df['predicted_gross_yield'] = (
            (df['predicted_rent'] * 12) / df['price'] *100
        )

        df = df.merge(
            df_counts,
            how='left',
            on='location'
        )

        df['market_ratio'] = df['count_rentals'] / df['count_sales']

        df['is_yield_focus'] = (
            (df['count_rentals'] > 0) & 
            (df['count_sales'] > 5) & 
            (df['market_ratio'] >= 0.1) &
            (df['price'] >= 200000) &
            (df['price'] <= 10000000)
        )

        save_parquet(df, self.gold_dir, "yield_overview_2.parquet")


