# src/utils/logger_config.py
"""
src/utils/logger_config.py
Configures logging for the app.
"""
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

def setup_logging(log_file="logs/pipeline.log"):
    os.makedirs("logs", exist_ok=True)
    
    # Create a logger object
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 1. Rotating File Handler (The "Black Box" recorder)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024, # 10MB
        backupCount=5
    )
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # 2. Stream Handler (The "Live View" in terminal)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_formatter = logging.Formatter('%(levelname)s: %(message)s')
    stream_handler.setFormatter(stream_formatter)

    # Add handlers to the logger
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)