"""
run_pipeline.py
Production-grade Master controller for the project.
"""
import json
import sys
import os
import logging
from datetime import datetime
import time, random

# 1. THE PATH FIX (Must be first)
from pathlib import Path

from src.modeling.rent_model import RentModel

root_path = str(Path(__file__).resolve().parent)
if root_path not in sys.path:
    sys.path.append(root_path)

# 2. THE IMPORTS
from src.inference.predict_rent import RentPredictor
from src.etl.gold_builder import GoldAnalyticsBuilder
from src.etl.transformer import PropertyTransformer
from src.utils.data_controller import load_config, save_parquet
from src.utils.logger_config import setup_logging
from src.etl.scraper import PropertyScraper

def main():
    # INITIALIZE LOGGING (The point of your import!)
    setup_logging()
    logger = logging.getLogger("MainPipeline")

    # # STEP 0: SCRAPE (The "E" in ETL)
    # logger.info("--- Phase 0: Scraping (Bronze Layer) ---")
    # scraper = PropertyScraper(base_url="https://www.property24.com")
    # scraper.run()

    # STEP 1: Transform Bronze to Silver 
    logger.info("--- Phase 1: ETL (Silver Layer) ---")
    transformer = PropertyTransformer()
    transformer.run()

    # STEP 2: Train Model (Optional: only run if you have new data)
    logger.info("--- Phase 2: Model Training ---")
    config = load_config('configs/model_config.yaml')
    trainer = RentModel(config)
    trainer.run()

    # STEP 3: Inference & Gold Layer
    logger.info("--- Phase 3: Analytics (Gold Layer) ---")
    
    predictor = RentPredictor("models/rent_price/production/prod_model_v1.joblib", config)
    predictor.predict_rent()

    gold_builder = GoldAnalyticsBuilder()
    gold_builder.build_market_overview(True)
    gold_builder.build_market_overview(False)
    gold_builder.build_sales_yield()

    logger.info("✅ Pipeline Execution Successful.")


if __name__ == "__main__":
    main()