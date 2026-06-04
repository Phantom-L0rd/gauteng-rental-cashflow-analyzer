"""
src/utils/state_tracker.py
"""
import json
import os
from datetime import datetime

class StateTracker:
    def __init__(self, file_path="state/global_state.json"):
        self.file_path = file_path
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {
            "last_scrape_date": None,
            "last_silver_update": None,
            "last_gold_update": None,
            "processed_bronze_files": []
        }

    def update(self, key, value):
        self.state[key] = value
        with open(self.file_path, 'w') as f:
            json.dump(self.state, f, indent=4)

    def is_already_done_today(self, key):
        """Checks if a specific task was already finished today."""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.state.get(key) == today