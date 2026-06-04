"""
src/utils/constants.py
This hold constants use throughout the app.
"""
MUNICIPALITY_MAP = {
    # City of Tshwane
    "pretoria": "City of Tshwane",
    "centurion": "City of Tshwane",
    "akasia": "City of Tshwane",
    "ga-rankuwa": "City of Tshwane",
    "soshanguve": "City of Tshwane",
    "mabopane": "City of Tshwane",
    "hammanskraal": "City of Tshwane",
    "temba": "City of Tshwane",
    "cullinan": "City of Tshwane",
    "bronkhorstspruit": "City of Tshwane",
    "wonderboom": "City of Tshwane",

    # City of Johannesburg
    "johannesburg": "City of Johannesburg",
    "sandton": "City of Johannesburg",
    "randburg": "City of Johannesburg",
    "roodepoort": "City of Johannesburg",
    "midrand": "City of Johannesburg",
    "soweto": "City of Johannesburg",
    "bedfordview": "City of Johannesburg",
    "eikenhof": "City of Johannesburg",
    "walkerville": "City of Johannesburg",

    # Ekurhuleni
    "alberton": "Ekurhuleni",
    "benoni": "Ekurhuleni",
    "boksburg": "Ekurhuleni",
    "brakpan": "Ekurhuleni",
    "kempton park": "Ekurhuleni",
    "germiston": "Ekurhuleni",
    "springs": "Ekurhuleni",
    "katlehong": "Ekurhuleni",
    "tembisa": "Ekurhuleni",
    "edenvale": "Ekurhuleni",
    "heidelberg": "Ekurhuleni",
    "nigel": "Ekurhuleni",

    # Sedibeng
    "vereeniging": "Sedibeng",
    "vanderbijlpark": "Sedibeng",
    "meyerton": "Sedibeng",
    "sebokeng": "Sedibeng",
    "evaton": "Sedibeng",
    "vaal marina": "Sedibeng",

    # West Rand
    "krugersdorp": "West Rand",
    "randfontein": "West Rand",
    "carletonville": "West Rand",
    "westonaria": "West Rand",
    "fochville": "West Rand",
}

# -----------------------------
# Constants for "Human" behavior
# -----------------------------
SAFE_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]