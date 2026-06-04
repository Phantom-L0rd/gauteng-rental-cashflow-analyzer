"""
src/utils/fetch_page.py
This handles request html page.
"""
import logging
import random
import time
import requests


from src.utils.constants import SAFE_AGENTS

# 1. Initialize global tools outside the function
# This keeps the "identity" consistent during the script run
session = requests.Session()

# -----------------------------
# Function for requesting html
# -----------------------------
def fetch_page(url):
    """Fetches HTML using a persistent session and rotating desktop headers."""
    
    # Check if we are still using a local session
    global session

    # 2. Build Stealth Headers
    # We rotate the User-Agent but keep it restricted to Desktop to avoid layout breaks
    headers = {
        "User-Agent": random.choice(SAFE_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.property24.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        # 3. Randomized Delay
        # Increased range slightly to be more "human"
        wait_time = random.uniform(1.2, 3.2)
        # logging.info(f"Waiting {wait_time:.2f}s before fetching...")
        time.sleep(wait_time)

        # 4. Perform the Request
        response = session.get(url, headers=headers, timeout=15)

        # 🟢 Success
        if response.status_code == 200:
            return response.text
            
        # 🟡 Page Specific Errors (Don't kill the whole script)
        if response.status_code == 404:
            logging.warning(f"📍 Suburb not found (404): {url}")
            return "SKIP" 

        # 🔴 Network/Block Errors (Panic mode)
        if response.status_code in [403, 429, 503]:
            logging.critical(f"🛑 BLOCK DETECTED ({response.status_code}) at {url}")
            return "BLOCK"

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Error: {e}")
    except requests.exceptions.ConnectionError:
        logging.error("Connection Error: Check your internet or if the server is down.")
    except Exception as e:
        logging.error(f"Unexpected error fetching {url}: {e}")
    
    return "BLOCK"