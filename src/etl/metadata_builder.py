"""
src/etl/metadata_builder.py
Used only to handle suburb look up table.
"""
import logging
import os
from bs4 import BeautifulSoup
import pandas as pd

from src.utils.data_controller import load_parquet, save_parquet
from src.utils.fetch_page import fetch_page
from src.utils.constants import MUNICIPALITY_MAP


def build_gauteng_lookup(base_url, province_name, province_id):
    logging.info(f"🚀 Starting scrape for: suburb list...")

    # 1. Scrape City and IDs from Gauteng Page
    cities = []

    url = f"{base_url}/to-rent/all-cities/{province_name.lower()}/{province_id}"
    html = fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")

    labels = soup.find_all('label', class_='checkbox')

    # 2. Loop through Cities to get Suburb IDs
    for label in labels:
        checkbox = label.find("input", {"name": "AllCityIds"})
        link_tag = label.find("a")

        if checkbox and link_tag:
            city_id = checkbox.get("value")
            name = link_tag.text.strip().lower()

            link = f"{base_url}/to-rent/all-suburbs/{name}/{province_name.lower()}/{city_id}"

            sec_html = fetch_page(link)
            sec_soup = BeautifulSoup(sec_html, "html.parser")
            if sec_soup:
                suburbs = sec_soup.find_all('label', class_='checkbox')
                for suburb in suburbs:
                    sec_checkbox = suburb.find("input", {"name": "AllSuburbIds"})
                    sec_link_tag = suburb.find("a")

                    if sec_checkbox and sec_link_tag:
                        suburb_id = sec_checkbox.get("value")
                        suburb_name = sec_link_tag.text.strip().lower()

                        cities.append({
                            "suburb_id":suburb_id,
                            "suburb_name":suburb_name,
                            "city_id":city_id,
                            "city_name":name,
                            "province_id":province_id,
                            "province_name":province_name
                        })
    
    # 3. Create DataFrame
    df = pd.DataFrame(cities)
    
    # 4. Map your dictionary
    df["municipality"] = (
        df["city_name"]
        .str.strip()
        .str.lower()
        .map(MUNICIPALITY_MAP)
        .fillna("Unknown")
    )

    df['last_scraped'] = None

    
    # 5. Save to the Metadata folder
    output_folder = "data/0_metadata"
    save_parquet(df, output_folder, "suburb_lookup.parquet")
    logging.info(f"✅ Metadata built with {len(df)} suburbs and {df['city_name'].nunique()} cities")
    return df

def get_suburb_list():
    if os.path.exists("data/0_metadata/suburb_lookup.parquet"):
        df =  load_parquet("data/0_metadata/suburb_lookup.parquet")
        # Check if the column exists, if not, create it
        if 'last_scraped' not in df.columns:
            df['last_scraped'] = None
        return df
    else:
        logging.error("🚨 Critical Error: No suburb metadata found!")
        return build_gauteng_lookup(base_url="https://www.property24.com", province_name="gauteng", province_id=1)