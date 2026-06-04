"""
src/etl/scraper.py
Production-grade extraction logic for Gauteng Property Data.
"""
import math
import os
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from datetime import datetime
# from fake_useragent import UserAgent
import pandas as pd
from src.etl.metadata_builder import get_suburb_list
from src.utils.data_controller import save_parquet
from src.utils.fetch_page import fetch_page


class PropertyScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.province_name = "gauteng"
        self.province_id = 1
        self.logger = logging.getLogger("Transformer")
        # We don't load it yet; we wait until we actually need it
        self._suburb_list = None 

    @property
    def suburb_list(self):
        """Only loads the list when you actually call scraper.suburb_list"""
        if self._suburb_list is None:
            self._suburb_list = get_suburb_list()
        return self._suburb_list

    def scrape_suburb_listings(self, suburb_id, suburb_name, city_name, rentals = True):
        """
        Main entry point. 
        listing_type can be 'to-rent' or 'for-sale'
        """
        all_listings = []
        
        sub_norm = suburb_name.lower().replace(' ', '-')
        city_norm = city_name.lower().replace(' ', '-')

        listing_type = 'to-rent' if rentals else 'for-sale'
        
        # Dynamic URL for Sale or Rent
        url = f"{self.base_url}/{listing_type}/{sub_norm}/{city_norm}/{self.province_name}/{suburb_id}"
        
        logging.info(f"🚀 Starting scrape for {suburb_name} ({listing_type})")
        
        html = fetch_page(f"{url}?PropertyCategory=House%2cApartmentOrFlat%2cTownhouse")
        if html == "BLOCK" or html == "SKIP" :
            return html

        soup = BeautifulSoup(html, "html.parser")

        # check if there is no listings in the page
        no_listing = soup.find('div', class_='p24_listingNotFound')

        if no_listing:
            return all_listings
        
        # Pagination Logic
        try:
            pager = soup.find('div', class_='p24_topPager')
            if pager:
                bold_spans = pager.find_all('span', class_='p24_bold')
                tot_num = int(bold_spans[-1].text.replace(' ', '')) # Handle space in "1 200"
                num_pages = math.ceil(tot_num / 20)
            else:
                num_pages = 1
        except Exception as e:
            logging.warning(f"Could not determine page count, defaulting to 1. Error: {e}")
            num_pages = 1

        # Loop Pages
        for i in range(1, num_pages + 1):
            page_url = f"{url}/p{i}?PropertyCategory=House%2cApartmentOrFlat%2cTownhouse"
            
            logging.info(f"📄 Scraping Page {i} of {num_pages}")

            if i > 1:
                html = fetch_page(page_url)
                if html == "BLOCK" or html == "SKIP" :
                    return html
                soup = BeautifulSoup(html, "html.parser")


            listing_cards = soup.find_all('div', class_='p24_tileContainer')

            if not listing_cards:
                logging.warning(f"No listings found on page {i} for {suburb_name}")
                break

            for card in listing_cards:
                l_num = card.get("data-listing-number")
                all_listings.append({
                    "listing_number" : l_num,
                    "scrape_at" : datetime.now().isoformat(),
                    "listing_data" : str(card)
                })
                
            # Respectful delay between search pages
            # time.sleep(random.uniform(2, 5))

        return all_listings
    
    # using Hive Path
    def save_to_bronze(self, data, suburb_id, munis, city, rentals=True):

        df = pd.DataFrame(data)
        # Construct Hive Path: data/1_bronze_raw/munis=.../city=.../
        munis_dir = f"munis={munis.lower().replace(' ', '_')}"
        city_dir = f"city={city.lower().replace(' ', '_')}"
        type_dir = f"type={"rent" if rentals else "sale"}"

        save_path = os.path.join("data", "1_bronze_raw", munis_dir, city_dir, type_dir)
        file_name = f"{suburb_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        save_parquet(df, save_path, file_name)
    
    def run(self):
        consecutive_blocks = 0

        if len(self.suburb_list) > 0:
            # 5. THE MASTER LOOP
            for row in self._suburb_list.itertuples(index=True):
                # --- 7-DAY RE-SCRAPE LOGIC ---
                should_scrape = True
                if hasattr(row, 'last_scraped') and row.last_scraped is not None:
                    try:
                        last_date = datetime.strptime(str(row.last_scraped), '%Y-%m-%d')
                        days_since = (datetime.now() - last_date).days
                        if days_since < 7:
                            should_scrape = False
                    except ValueError:
                        should_scrape = True # If date format is weird, just scrape it
                
                if not should_scrape:
                    continue


                # --- START SCRAPING ---
                today_str = datetime.now().strftime('%Y-%m-%d')
                self.logger.info(f"📍 Processing {row.suburb_name} in {row.city_name} (Last: {row.last_scraped})")

                can_update = True

                # We process Rental and Sale in a list to avoid repeating code
                for is_rental in [True, False]:
                    mode = "Rentals" if is_rental else "Sales"
                    try:
                        data = self.scrape_suburb_listings(
                            suburb_id=row.suburb_id, 
                            suburb_name=row.suburb_name, 
                            city_name=row.city_name,
                            rentals=is_rental
                        )

                        if data == "BLOCK":
                            consecutive_blocks += 1
                            if consecutive_blocks >= 3:
                                self.logger.critical("🚨 3 Consecutive blocks. Aborting.")
                                # Save progress before dying
                                save_parquet(self._suburbs_, "data/0_metadata" ,"suburb_lookup.parquet")
                                return # Exit function
                            
                            wait = 60 * consecutive_blocks
                            self.logger.warning(f"⏳ Blocked! Sleeping {wait}s...")
                            time.sleep(wait)
                            can_update = False
                            break # Break the Rental/Sale loop to move to next suburb or exit
                        
                        elif data == "SKIP" or data is None:
                            consecutive_blocks = 0 
                            continue # Move to next (Sale if Rental failed)

                        # SUCCESS
                        consecutive_blocks = 0
                        self.save_to_bronze(
                            data=data,
                            suburb_id=row.suburb_id,
                            munis=row.municipality,
                            city=row.city_name,
                            rentals=is_rental
                        )

                    except Exception as e:
                        consecutive_blocks += 1
                        self.logger.error(f"❌ Critical error on {row.suburb_name} {mode}: {e}")

                # Update the date only after both (or attempted both) are done
                if can_update:
                    self._suburb_list.at[row.Index, 'last_scraped'] = today_str
                else:
                    self.logger.error(f"❌ Cannot update scraping for {row.suburb_name} : rentals or sales not scrape")

                # Safety Check
                if consecutive_blocks >= 3:
                    break

                # Periodically save metadata (Every 5 suburbs)
                if row.Index % 5 == 0:
                    save_parquet(self._suburb_list, "data/0_metadata" ,"suburb_lookup.parquet")
                    
                # time.sleep(random.uniform(5, 10))
        save_parquet(self._suburb_list, "data/0_metadata" ,"suburb_lookup.parquet")