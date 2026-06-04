"""
src/utils/data_controller.py
This handle all data saving and loading.
"""
import pandas as pd
import pyarrow
import os
import logging
import yaml

def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)
    return None

def save_config(path, config):
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

def save_parquet(df, folder_path, file_name):
    # Combine them safely into one path
    full_path = os.path.join(folder_path, file_name)
    
    try:
        # Create folders if they don't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        df.to_parquet(full_path, engine='pyarrow', compression='snappy', index=False)
        logging.info(f"💾 Saved: {full_path}")
    except Exception as e:
        logging.error(f"❌ Save failed for {file_name}: {e}")

def load_parquet(file_path):
    try:
        df = pd.read_parquet(file_path)
        return df
    except Exception as e:
        logging.error(f"❌ Failed to load file {file_path}: {e}")
        return None

