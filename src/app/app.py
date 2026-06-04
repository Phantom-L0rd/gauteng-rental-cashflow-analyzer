"""
src/app.py
Strreamlit app entry point.
"""
import streamlit as st
import sys
from pathlib import Path

# Get the absolute path to the 'project-real-estate' folder
root_path = str(Path(__file__).resolve().parents[2])
if root_path not in sys.path:
    sys.path.append(root_path)

from src.utils.data_controller import load_parquet
from src.utils.logger_config import setup_logging
# from utils.calculations import load_models

def apply_custom_style():
    st.markdown("""
        <style>
        /* Main background */
        .stApp { background-color: black; }
        
        /* Modern Metric Cards */
        [data-testid="stMetricValue"] { font-size: 28px; color: white; }
        div[data-testid="stMetric"] {
            background-color: black;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-bottom: 4px solid #3B82F6;
        }
        
        /* Sidebar customization */
        section[data-testid="stSidebar"] { background-color: grey; }
        section[data-testid="stSidebar"] .stMarkdown { color: white; }
        </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 1. App Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Real Estate Investment Intelligence",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)
# apply_custom_style()
setup_logging()

# --------------------------------------------------
# 2. Global Metadata
# --------------------------------------------------
APP_METADATA = {
    "app_name": "Real Estate Market Analytics & Investment Platform",
    "description": (
        "A data-driven platform for analysing the residential real estate market, "
        "evaluating investment opportunities, and forecasting rental returns."
    ),
    "data_source": "Public property listings (aggregated)",
    "last_updated": "2026-01-01",
    "model_version": "v0.1",
    "disclaimer": (
        "This application is for educational and analytical purposes only. "
        "Predictions are probabilistic and not financial advice."
    ),
}

# --------------------------------------------------
# 3. Cached Data & Model Loading
# --------------------------------------------------
@st.cache_data(show_spinner="Loading market data...")
def load_data():
    df_rentals = load_parquet("data/3_gold_analytics/market_overview_rent.parquet")
    df_sales = load_parquet("data/3_gold_analytics/market_overview_sale.parquet")
    df_yield = load_parquet("data/3_gold_analytics/yield_overview_2.parquet")
    return df_rentals, df_sales, df_yield


# @st.cache_resource(show_spinner="Loading models...")
# def load_ml_models():
#     return load_models()


# processed_data, feature_data = load_data()
# models = load_ml_models()

df_rentals, df_sales, df_yield = load_data()

# --------------------------------------------------
# 4. Session State Initialization
# --------------------------------------------------
DEFAULT_SESSION_STATE = {
    "selected_properties": [],
    "risk_tolerance": "Medium",
    "investment_horizon": 5,
    "yield_investment": True,
    "financing":True,
    # "location_filter": "All",
    # "property_type_filter": "All",
    "scenario": "Base"
}

for key, value in DEFAULT_SESSION_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

if "df_rentals" not in st.session_state:
    st.session_state.df_rentals = df_rentals

if "df_sales" not in st.session_state:
    st.session_state.df_sales = df_sales

if "df_yield" not in st.session_state:
    st.session_state.df_yield = df_yield

# --------------------------------------------------
# 5. Sidebar (Global Context)
# --------------------------------------------------
with st.sidebar:
    st.title("🏠 Real Estate Analytics")

    st.markdown(APP_METADATA["description"])

    st.divider()

    st.subheader("Global Filters")

    # st.session_state.location_filter = st.selectbox(
    #     "Location",
    #     options=["All"] + sorted(df["location"].unique().tolist()),
    # )

    # st.session_state.property_type_filter = st.selectbox(
    #     "Property Type",
    #     options=["All"] + sorted(df["type"].unique().tolist()),
    # )
    st.session_state.yield_investment = st.checkbox("Yield investment", value=st.session_state.yield_investment)

    st.session_state.financing = st.checkbox("Is financing?", value=st.session_state.financing)

    st.session_state.risk_tolerance = st.selectbox(
        "Risk Tolerance",
        options=["Low", "Medium", "High"],
    )

    st.session_state.investment_horizon = st.slider(
        "Investment Horizon (years)",
        min_value=1,
        max_value=10,
        value=st.session_state.investment_horizon,
    )

    st.divider()

    st.caption(f"📊 Data last updated: {APP_METADATA['last_updated']}")
    st.caption(f"🤖 Model version: {APP_METADATA['model_version']}")

# --------------------------------------------------
# 6. Main Landing Content
# --------------------------------------------------
st.title(APP_METADATA["app_name"])

st.markdown(
    """
### How to use this app

1. **Overview** – Understand the current real estate market
2. **Investment Finder** – Discover high-potential investment opportunities
3. **Property Comparison** – Compare properties side by side
4. **Investment Calculator** – Run what-if financial scenarios
5. **Forecasting** – Explore rental price and ROI predictions

Use the **sidebar filters** to set your global context.
"""
)

# import sys
# st.write(sys.executable)


st.info(APP_METADATA["disclaimer"])

# --------------------------------------------------
# 7. Footer
# --------------------------------------------------
st.divider()
st.caption(
    "Built with open-source tools • Streamlit • Python • Data Science & Analytics"
)
st.caption("Author: Arop Kuol • GitHub: https://github.com/yourusername")
