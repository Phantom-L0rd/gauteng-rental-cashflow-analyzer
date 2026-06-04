"""
src/etl/feature_builder.py
Cleans and feature engineer data for modelling
"""
import pandas as pd
import glob
import os
import logging

from src.utils.data_controller import load_parquet, save_parquet

class FeatureBuilder:
    def __init__(self, is_rentals=True):
        self.silver_dir = "data/2_silver_cleaned"
        self.feat_dir = "data/4_feature_store"
        self.logger = logging.getLogger("FeatureBuilder")
        self.is_rentals = is_rentals

    def select_features(self, df):
        features = [
            "bedrooms",
            "bathrooms",
            "parking",
            "floor_size",
            "suburb_avg_rent",
            "is_estate",
            "has_security",
            "is_modern",
            "type"
        ]

        return df[features + ["price"]] if self.is_rentals else df[features]

    def save_feature_store(self, df):
        save_parquet(df, self.feat_dir, "rental_features.parquet")
    
    def get_preprocessed_sales_data(self):
        self.logger.info("Preprocessing sales data...")
        df = self.load_silver_data()
        df = self.basic_cleaning(df)
        df = self.feature_engineering(df)
        df = self.smart_imputation(df)
        return df

    def prepare_preprocessed_rental_data(self):
        self.logger.info("Getting data ready for modelling...")
        df = self.load_silver_data()
        df = self.basic_cleaning(df)
        df = self.feature_engineering(df)
        df = self.smart_imputation(df)
        df = self.select_features(df)
        self.save_feature_store(df)
        self.logger.info("Data has been cleaned and feature engineered")
    