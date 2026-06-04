import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(
    page_title="Investment Calculator",
    layout="wide"
)

st.title("💰 Investment Calculator")

# ---------------------------
# 1. User Inputs
# ---------------------------
st.header("Scenario Inputs")
# TODO: Purchase price input
# TODO: Deposit amount input
# TODO: Loan interest rate input
# TODO: Loan term input
# TODO: Operating costs input
# TODO: Vacancy rate input
# TODO: Rental growth assumption

# ---------------------------
# 2. Scenario Selection
# ---------------------------
st.header("Scenario Presets")
# TODO: Radio buttons for Conservative / Base / Aggressive

# ---------------------------
# 3. Output Metrics
# ---------------------------
st.header("Calculated Outputs")
# TODO: Monthly cashflow
# TODO: Annual net return
# TODO: Break-even year
# TODO: IRR

# ---------------------------
# 4. Notes / Interpretation
# ---------------------------
st.subheader("Interpretation Notes")
st.write("""
- Results are highly sensitive to assumptions
- Financing terms significantly affect returns
- IRR is useful for scenario comparison
""")
