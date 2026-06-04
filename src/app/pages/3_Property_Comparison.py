import streamlit as st
import pandas as pd
import numpy as np
# import altair as alt

import sys
from pathlib import Path


# Get the absolute path to the 'project-real-estate' folder
root_path = str(Path(__file__).resolve().parents[2])
if root_path not in sys.path:
    sys.path.append(root_path)

st.set_page_config(
    page_title="Property Comparison Tool",
    layout="wide"
)

st.title("📊 Property Comparison")


# ---------------------------
# 1. Property Selection
# ---------------------------
st.header("Select Properties")
# TODO: Multi-select dropdown or table to choose properties

# ---------------------------
# 2. Comparison Metrics
# ---------------------------
st.header("Metrics Comparison")
# TODO: Table of purchase price, rental income, NOI, yield, ROI, risk score

# ---------------------------
# 3. Visual Comparison
# ---------------------------
st.header("Visual Comparison")
# TODO: Bar chart for yield and ROI
# TODO: Radar chart for risk profile
# TODO: Cashflow projection charts

# ---------------------------
# 4. Summary Insights
# ---------------------------
st.subheader("Key Insights")
st.write("""
- Best cashflow option
- Best appreciation potential
- Lowest risk option
""")
