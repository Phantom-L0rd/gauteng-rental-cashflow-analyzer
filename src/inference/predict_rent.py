from datetime import datetime
import json
import os
import joblib
import pandas as pd
import logging

from src.utils.data_controller import load_parquet, save_parquet

class RentPredictor:
    def __init__(self, model_path, config):
        self.logger = logging.getLogger("RentPredictor")
        self.model = joblib.load(model_path)
        self.config = config

    def predict_rent(self):
        df = load_parquet('data/2_silver_cleaned/type=sale/listings.parquet')
        numerical = self.config["features"]["numerical"]
        categorical = self.config["features"]["categorical"]
        target_col = self.config['target']
        df_processed = df[numerical+categorical+[target_col]]
        preds = self.model.predict(df_processed)

        df["predicted_rent"] = preds

        self.save_to_gold(df)
    
    def save_to_gold(self, df):
        gold_dir = "data/3_gold_analytics/sales"
        os.makedirs(gold_dir, exist_ok=True)
        
        file_name = f"predicted_rent.parquet"
        save_parquet(df, gold_dir, file_name)
