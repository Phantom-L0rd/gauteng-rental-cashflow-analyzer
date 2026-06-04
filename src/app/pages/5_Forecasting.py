import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(
    page_title="Forecasting",
    layout="wide"
)

st.title("📈 Forecasting & Outlook")

# ---------------------------
# 1. Rental Price Forecast
# ---------------------------
st.header("Rental Price Projections")
# TODO: Plot predicted rent over 1–5 years
# TODO: Show confidence intervals

# ---------------------------
# 2. Model Overview
# ---------------------------
st.header("Model Overview")
# TODO: Describe model used (simple text or expanders)

# ---------------------------
# 3. Stress Scenarios
# ---------------------------
st.header("Stress Scenarios")
# TODO: Interest rate increase scenario
# TODO: Demand contraction scenario
# TODO: Economic slowdown scenario

# ---------------------------
# 4. Limitations & Notes
# ---------------------------
st.subheader("Important Notes")
st.write("""
- Forecasts are probabilistic
- Structural shifts may invalidate predictions
- Accuracy decreases with forecast horizon
""")
