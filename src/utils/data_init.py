import streamlit as st
import pandas as pd

@st.cache_data(show_spinner="Loading market data...")
def load_data():
    data = [
        {
            "link" : "https://www.property24.com/for-sale/arcadia/pretoria/gauteng/301/107631563",
            "location" : "Arcadia",
            "type" : "Apartment",
            "bedrooms" : 2.0,
            "bathrooms" : 2.0,
            "parking" : 1.0,
            "floor_size" : 64.0,
            "C" : 1_250_000.00,
            "levies" : 1900.00,
            "rates_taxes" :950.00
        },
        {
            "link" : "https://www.property24.com/for-sale/arcadia/pretoria/gauteng/301/116702457",
            "location" : "Arcadia",
            "type" : "Apartment",
            "bedrooms" : 2.0,
            "bathrooms" : 1.0,
            "parking" : 1.0,
            "floor_size" : 78,
            "sale_price" : 550_000.00,
            "levies" : 2384.00,
            "rates_taxes" :389.00
        },
        {
            "link" : "i dont know",
            "location" : "Arcadia",
            "type" : "Apartment",
            "bedrooms" : 2.5,
            "bathrooms" : 2.0,
            "parking" : 1.0,
            "floor_size" : 88,
            "sale_price" : 525_000.00,
            "levies" : 1888.00,
            "rates_taxes" :434.00
        },
        {
            "link" : "https://www.property24.com/for-sale/brooklyn/pretoria/gauteng/614/116531184?plId=2243402&plt=3&plsIds=2263225",
            "location" : "Brooklyn",
            "type" : "Townhouse",
            "bedrooms" : 3.0,
            "bathrooms" : 3.5,
            "parking" : 2.0,
            "floor_size" : 350.0,
            "sale_price" : 2_350_000.00,
            "levies" : 2900.00,
            "rates_taxes" :2084.00
        },
        {
            "link" : "https://www.property24.com/to-rent/ashlea-gardens/pretoria/gauteng/235/116696639?uaid=40087192&utm_source=alert&utm_medium=email&utm_campaign=portalemailalerts",
            "location" : "Ashlea Gardens",
            "type" : "Townhouse",
            "bedrooms" : 3.0,
            "bathrooms" : 2.0,
            "parking" : 2.0,
            "floor_size" : 180.0,
            "sale_price" : 1_985_000.00,
            "levies" : 3063.00,
            "rates_taxes" :1123.00
        },
        {
            "link" : "https://www.property24.com/to-rent/ashlea-gardens/pretoria/gauteng/235/116696639?uaid=40087192&utm_source=alert&utm_medium=email&utm_campaign=portalemailalerts",
            "location" : "Ashlea Gardens",
            "type" : "Townhouse",
            "bedrooms" : 3.0,
            "bathrooms" : 2.5,
            "parking" : 4.0,
            "floor_size" : 230.0,
            "sale_price" : 3_385_000.00,
            "levies" : 3463.00,
            "rates_taxes" :1823.00
        },
    ]

    return pd.DataFrame(data)