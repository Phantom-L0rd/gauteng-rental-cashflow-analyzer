import streamlit as st
import pandas as pd
import numpy as np

# import altair as alt

st.set_page_config(
    page_title="Investment Finder",
    layout="wide"
)

# ---------------------------
# Load data
# ---------------------------
data = st.session_state.df_yield


def calculate_alpha_score(
    price, 
    predicted_rent, 
    has_solar, 
    has_security, 
    property_price_m2, 
    suburb_avg_price_m2,
    weights={'yield': 0.5, 'resilience': 0.3, 'value': 0.2}
):
    """
    Calculates a normalized score from 0-100 representing investment quality.
    """
    # 1. Yield Component (Higher is better)
    # Average Gauteng yield is ~7-8%. We normalize 0% to 15% as 0 to 1.
    gross_yield = (predicted_rent * 12) / price
    yield_score = min(max(gross_yield / 0.15, 0), 1)
    
    # 2. Resilience Component (Binary/Categorical)
    # Solar is a massive 2026 requirement.
    resilience_score = (0.7 if has_solar else 0) + (0.3 if has_security else 0)
    
    # 3. Price Value Component (Lower price/m2 vs suburb average is better)
    # If property_m2 is 80% of suburb_avg, that's a 20% discount (Value!)
    price_ratio = property_price_m2 / suburb_avg_price_m2
    # We invert it: if ratio is 0.8, score is high. if ratio is 1.5, score is 0.
    value_score = min(max(2 - price_ratio, 0), 1) 
    
    # Final Weighted Calculation
    alpha_score = (
        (yield_score * weights['yield']) +
        (resilience_score * weights['resilience']) +
        (value_score * weights['value'])
    ) * 100
    
    return round(alpha_score, 2)

st.title("🔍 Investment Finder")


st.sidebar.header("Investment Strategy Weights")
w_yield = st.sidebar.slider("Yield Weight (Income)", 0.0, 1.0, 0.5)
w_res = st.sidebar.slider("Resilience Weight (Solar/Security)", 0.0, 1.0, 0.3)
w_val = st.sidebar.slider("Value Weight (Price/m2)", 0.0, 1.0, 0.2)

# Ensure weights sum to 1.0 for mathematical sanity
total_w = w_yield + w_res + w_val
weights = {
    'yield': w_yield / total_w,
    'resilience': w_res / total_w,
    'value': w_val / total_w
}

# Example display for a property
score = calculate_alpha_score(1500000, 12000, True, True, 14000, 16500, weights)

st.metric(label="Investment Alpha Score", value=f"{score}/100")

if score > 75:
    st.success("🔥 High Alpha: This property is a Strong Buy based on your criteria.")
elif score > 50:
    st.info("⚖️ Neutral: Fair market value.")
else:
    st.warning("⚠️ Low Alpha: Potential money pit or overpriced for the area.")


# ---------------------------
# 1. User Inputs
# ---------------------------
st.header("Filter Criteria")
# TODO: Budget slider
# TODO: Target yield slider
# TODO: Risk tolerance dropdown
# TODO: Investment horizon slider
# TODO: Location and property type filters

# ---------------------------
# 2. Investment Scoring
# ---------------------------
st.header("Investment Score")
# TODO: Show ranked list of properties
# TODO: Score breakdown per property

st.dataframe(data)

# ---------------------------
# 3. Transparency & Caution
# ---------------------------
st.subheader("Important Notes")
st.write("""
- Scores are sensitive to assumptions
- Weightings reflect general investment preferences
- Rankings are decision support only
""")
