"""
src/etl/transformer.py (Placeholder logic)
"""
from datetime import datetime
import logging
import re
import os
from bs4 import BeautifulSoup
import pandas as pd
import glob

from src.etl.metadata_builder import get_suburb_list
from src.utils.data_controller import load_parquet, save_parquet

class PropertyTransformer:
    def __init__(self):
        self.bronze_dir = "data/1_bronze_raw"
        self.silver_dir = "data/2_silver_cleaned"
        self.feat_dir = "data/4_feature_store"
        self._suburb_list = None
        self.logger = logging.getLogger("Transformer")
    
    @property
    def suburb_list(self):
        """Only loads the list when you actually call scraper.suburb_list"""
        if self._suburb_list is None:
            self._suburb_list = get_suburb_list()
        return self._suburb_list

    def clean_numeric(self, text, floor_size=None):
        """
        Cleans strings like 'R 8 500', '1.5 ha', or 'R 150 / m²' into floats.
        
        Args:
            text (str): The raw text from HTML.
            floor_size (float): Optional floor size used to calculate total price 
                               if the listing is 'per m²'.
        """
        if not text:
            return None
        
        text = text.lower().strip()
        
        # Handle Hectares (1 ha = 10,000 m²)
        if 'ha' in text:
            try:
                num = re.search(r"(\d+\.?\d*)", text).group(1)
                return float(num) * 10000
            except (ValueError, AttributeError):
                return None

        # Handle Price per m² (Common in Commercial/Large Sales)
        multiplier = 1.0
        if 'per' in text or '/' in text:
            multiplier = floor_size if floor_size else 1.0

        # Extract digits and decimals only
        nums = re.sub(r'[^\d.]', '', text.replace(' ', ''))
        try:
            return float(nums) * multiplier if nums else None
        except ValueError:
            return None

    def get_flags(self, description, suburb):
        """
        Binary feature engineering from the description snippet.
        Helps the model identify 'Premium' or 'Budget' features.
        """
        desc = description.lower()

        # 1. Infer Estate Status
        is_estate = 1 if "estate" in desc else 0
        if any(x in suburb for x in ['estate', 'manor', 'village', 'golf', 'villas']):
            is_estate = 1
        
        # 2. Infer Security (High probability in Gauteng Estates)
        has_security = 1 if any(x in desc for x in ['guard', 'electric fence', 'cctv', 'secure']) else 0
        if is_estate == 1:
            has_security = 1 # Safe assumption for Gauteng gated communities

        # 3. Infer Modern/Luxury from Title
        is_modern = 1 if any(x in desc for x in ["modern", "newly", "renovated", 'upmarket', 'luxury']) else 0

        return {
            "is_estate": is_estate,
            "has_security": has_security,
            "is_modern":  is_modern
        }
    
    def get_property_type(self, text):
        """
        Feature engineering from title to get property type.
        """
        if text in ['Commercial Property', 'Industrial Property']:
            return text
        if 'Apartment' in text:
            return 'Apartment'
        if 'Townhouse' in text:
            return 'Townhouse'
        if 'House' in text:
            return 'House'
        return text

    def extract_features_from_html(self, html_string, scrape_time, suburb, city, munis):
        """
        Parses a single HTML card into a clean dictionary.
        """
        if not html_string:
            return None
        
        soup = BeautifulSoup(html_string, 'html.parser')
        
        # Property ID (from the link)
        link_tag = soup.find('a', href=True)
        prop_id = link_tag['href'].split('/')[-1].split('?')[0] if link_tag else None
        
        title_tag = soup.select_one(".p24_title")
        title = title_tag.text.strip() if title_tag else None

        prop_type = self.get_property_type(title) if title else None
        
        # 1. Size must be extracted first to help clean 'Price per m2'
        size_tag = soup.select_one(".p24_size")
        floor_size = self.clean_numeric(size_tag.text if size_tag else None)

        # 2. Extract Price
        price_tag = soup.select_one(".p24_price")
        price = self.clean_numeric(price_tag.text if price_tag else None, floor_size)
        
        # 3. Extract Icons (Beds, Baths, Parking)
        features = {f.get('title', '').lower(): f.find('span').text.strip() 
                    for f in soup.find_all('span', class_='p24_featureDetails') if f.find('span')}

        # 4. Extract Snippet Text
        excerpt_tag = soup.select_one(".p24_excerpt")
        description = excerpt_tag.text.strip() if excerpt_tag else ""

        return {
            "listing_number": prop_id,
            "scrape_at": scrape_time,
            "price": price,
            "title": title,
            "type": prop_type,
            "suburb": suburb,
            "city": city,
            "munis":munis,
            "bedrooms": self.clean_numeric(features.get("bedrooms")),
            "bathrooms": self.clean_numeric(features.get("bathrooms")),
            "parking": self.clean_numeric(features.get("parking spaces")),
            "floor_size": floor_size,
            **self.get_flags(description, suburb)
        }

    def process_bronze_data(self, rentals = True, force_run = False):
        """
        The Main Pipeline: 
        1. Finds all raw Parquet files.
        2. Cleans and transforms them.
        3. Deduplicates based on listing_number.
        """

        self.logger.info(f"🔄 Starting Silver Transformation for {'Rentals' if rentals else 'Sales'}")
        
        listing_type = "rent" if rentals else "sale"

        all_listings = []

            
        # Use glob to find all files for this muni/type across all cities
        bronze_glob = f"{self.bronze_dir}/munis=*/city=*/type={listing_type}/*.parquet"
        files = glob.glob(bronze_glob)
        

        if files:
            for file in files:
                # Extract Suburb ID from filename (format: ID_TIMESTAMP.parquet)
                try:
                    file_name = os.path.basename(file)
                    suburb_id = file_name.split('_')[0]
                    
                    # Metadata Lookup
                    meta_match = self.suburb_list[self.suburb_list['suburb_id'] == suburb_id]
                    if meta_match.empty:
                        continue
                        
                    sub_name = meta_match['suburb_name'].values[0]
                    city_name = meta_match['city_name'].values[0]
                    muni = meta_match['municipality'].values[0].lower()


                    df_raw = load_parquet(file)
                    
                    for row in df_raw.itertuples():
                        clean_data = self.extract_features_from_html(
                            row.listing_data, row.scrape_at, sub_name, city_name, muni
                        )
                        if clean_data:
                            all_listings.append(clean_data)

                except Exception as e:
                    self.logger.error(f"❌ Error processing file {file}: {e}")

        if all_listings:
            df_silver = pd.DataFrame(all_listings)

            df_silver['scrape_at'] = pd.to_datetime(df_silver['scrape_at'], format='ISO8601')

            df_clean = self.clean_listings(df_silver,rentals=rentals)

            self.save_to_silver_layer(df_clean, rentals)

    
    def build_rent_avgs(self, df):
        suburb_means = df.groupby('location')['price'].mean()
        suburb_means = suburb_means.reset_index()
        suburb_means.columns = ['location', 'suburb_avg_rent']
        save_parquet(suburb_means, self.feat_dir, "suburb_avgs.parquet")

        city_means = df.groupby('city')['price'].mean()
        city_means = city_means.reset_index()
        city_means.columns = ['city', 'city_avg_rent']
        save_parquet(city_means, self.feat_dir, "city_avgs.parquet")

        muni_means = df.groupby('munis')['price'].mean()
        muni_means = muni_means.reset_index()
        muni_means.columns = ['munis', 'muni_avg_rent']
        save_parquet(muni_means, self.feat_dir, "muni_avgs.parquet")

    
    def clean_listings(self, df, rentals = True):
        """
        Clean and feature engineer listings
        """
        df = df.sort_values('scrape_at', ascending=False).drop_duplicates('listing_number')

        # filter extreme values
        df = df[
            ((df['bedrooms'] <= 10) | (df['bedrooms'].isna())) &
            ((df['bathrooms'] <= 10) | (df['bathrooms'].isna())) &
            ((df['parking'] <= 20) | (df['parking'].isna())) &
            # (((df['floor_size'] >= 20) & (df['floor_size'] <= 2000)) | (df['floor_size'].isna())) &
            ((df['floor_size'] <= 2000) | (df['floor_size'].isna()))
        ]

        # filter porperty type
        df = df[df['type'].isin(['Apartment', 'House', 'Townhouse'])]

        # Fill missing Beds/Baths with most common (mode)
        df['bedrooms'] = df.groupby(['type'])['bedrooms'].transform(
            lambda x: x.fillna(x.mode()[0] if not x.mode().empty else df['bedrooms'].mode()[0])
        )
        df['bathrooms'] = df.groupby(['type'])['bathrooms'].transform(
            lambda x: x.fillna(x.mode()[0] if not x.mode().empty else df['bathrooms'].mode()[0])
        )
        df['parking'] = df.groupby(['type'])['parking'].transform(
            lambda x: x.fillna(x.mode()[0] if not x.mode().empty else df['parking'].mode()[0])
        )
        # df['parking'] = df['parking'].fillna(0)
        # create key for location
        df['location'] = (
            df['suburb'].str.lower().str.replace(' ', '_') + 
            '_' + 
            df['city'].str.lower().str.replace(' ', '_')
        )

        # Total rooms
        df["total_rooms"] = df["bedrooms"] + df["bathrooms"]
        
        # df = df[df['floor_size'] >= 10]

        # Smart Imputation for Floor Size
        # 1️⃣ Most granular: location + total_rooms
        mask = df['floor_size'].isna()
        med_1 = df.groupby(['location', 'total_rooms'])['floor_size'].transform('median')
        df.loc[mask, 'floor_size'] = med_1[mask]

        # 2️⃣ Fallback: location only
        mask = df['floor_size'].isna()
        med_2 = df.groupby('location')['floor_size'].transform('median')
        df.loc[mask, 'floor_size'] = med_2[mask]

        # 3️⃣ Fallback: total_rooms only
        mask = df['floor_size'].isna()
        med_3 = df.groupby('total_rooms')['floor_size'].transform('median')
        df.loc[mask, 'floor_size'] = med_3[mask]

        # 4️⃣ Final fallback: global median
        global_median = df['floor_size'].median()
        df['floor_size'] = df['floor_size'].fillna(global_median)

        if rentals:
            df = df[(df['price'] >= 2500) & (df['price'] <= 150000)]
        
        df = df.dropna(subset=['price'])

        #apply Z-score to price
        df['price_sqm'] = df['price'] / df['floor_size']
        df['z_score'] = df.groupby('location')['price_sqm'].transform(lambda x: (x - x.mean()) / x.std())
        df = df[df['z_score'].abs() <= 2.5]

        # Target Encoding for suburb (mean rent per suburb)
        if rentals:
            self.build_rent_avgs(df)

        suburb_means = load_parquet(f"{self.feat_dir}/suburb_avgs.parquet")
        city_means = load_parquet(f"{self.feat_dir}/city_avgs.parquet")
        muni_means = load_parquet(f"{self.feat_dir}/muni_avgs.parquet")

        df = df.merge(
            suburb_means,
            on="location",
            how="left"
        )
        df = df.merge(
            city_means,
            on="city",
            how="left"
        )
        df = df.merge(
            muni_means,
            on="munis",
            how="left"
        )

        df['is_luxury'] = (df['suburb_avg_rent'] >= 30000).astype(int)
        
        return df

    def save_to_silver_layer(self, df, rentals=True):
        """Saves the cleaned municipality data to the Silver folder."""
        type_str = "rent" if rentals else "sale"
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
        
        save_path = os.path.join(self.silver_dir, f"type={type_str}")
        file_name = f"listings.parquet" # We save as a master file per muni

        save_parquet(df, save_path, file_name)
        self.logger.info(f"💾 Saved {len(df)} cleaned listings for {type_str}")

    def run(self, force_run = False):
        self.process_bronze_data(rentals=True, force_run=force_run)
        self.process_bronze_data(rentals=False, force_run=force_run)
