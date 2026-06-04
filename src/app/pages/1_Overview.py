import pandas as pd
import streamlit as st
import plotly.express as px
import json
# import geopandas as gpd

import sys
from pathlib import Path

# Get the absolute path to the 'project-real-estate' folder
root_path = str(Path(__file__).resolve().parents[2])
if root_path not in sys.path:
    sys.path.append(root_path)


st.set_page_config(
    page_title="Market Overview",
    page_icon="🏠",
    layout="wide"
)

# ---------------------------
# Load data
# ---------------------------

df_rentals = st.session_state.df_rentals.copy()
df_yield = st.session_state.df_yield.copy()



# ---------------------------
# 1. Filters
# ---------------------------
# TODO: Filter by location, property type, bedrooms
# TODO: Add tables or charts


munis = df_rentals['munis'].unique()
filtered_rentals = df_rentals.copy()
filtered_sales = df_yield.copy()


with st.sidebar:
    st.header("Filters")
    muni_choice = st.selectbox("Select Municipality", ["All", *munis])
    # loc_filter = st.multiselect(
    #     "Location",
    #     options=sorted(df["location"].unique().tolist()),
    # )
    # type_filter = st.multiselect(
    #     "Property Type",
    #     key='type_filter',
    #     options=sorted(df["type"].unique().tolist()),
    # )
    # beds = {
    #     "1+": 1, "2+":2, "3+":3, "4+":4, "5+":5
    #     }
    # bed_filter = st.selectbox(
    #     "Bedrooms",
    #     key="bed_filter",
    #     options=beds.keys()
    # )

# if loc_filter:
#     filtered_df = filtered_df[filtered_df['location'].isin(loc_filter)]

# if type_filter:
#     filtered_df = filtered_df[filtered_df['type'].isin(type_filter)]

# if bed_filter:
#     filtered_df = (filtered_df[filtered_df['bedrooms']>=beds[bed_filter]])

if muni_choice != 'All':
    filtered_rentals = filtered_rentals[filtered_rentals['munis'].str.contains(muni_choice)].copy()
    filtered_sales = filtered_sales[filtered_sales['munis'].str.contains(muni_choice.lower())].copy()

filtered_sales = filtered_sales[filtered_sales['is_yield_focus']==st.session_state.yield_investment].copy()


st.title(f"🇿🇦 {"Gauteng" if muni_choice == 'All' else muni_choice} Property Market Overview")

# ---------------------------
# 2. Market Summary Metrics
# ---------------------------
# st.header("Market Summary" if muni_choice == 'All' else f"Market Summary for {muni_choice}")
# TODO: Add KPIs like median rental price, median property price, Price per square meter, gross yield


# total_props = len(filtered_df)

# Median rental price
med_rental = filtered_rentals['median_price'].median()

# Median property price
med_price = filtered_sales['price'].median()

# Avg property price
avg_price = filtered_sales['price'].mean()

# Price per square meter
price_per_sqm = (
    (filtered_sales['price'] / filtered_sales['floor_size']).mean()
)

# Avg gross yield
gross_yield = (
    filtered_sales['predicted_gross_yield'].mean()
)

# med_rental = 11000

# med_price = (
#     filtered_df['sale_price'].mean()
#     if total_props > 0 else 0
# )

# gross_yield = 0

kpi1, kpi2, kpi4, kpi5 = st.columns(4, border=True)


kpi1.metric("Median Rental Price", f"R{med_rental:,.2f}")
kpi2.metric("Median Property Price", f"R{med_price:,.2f}")
kpi4.metric("Avg Price per square meter",f"R{price_per_sqm:,.2f}")
kpi5.metric("Avg Gross yield", f"{gross_yield:.2f}%")

# # Metric Row
# col1, col2, col3 = st.columns(3)
# col1.metric("Suburbs Tracked", len(filtered_df))
# col2.metric("Median Rent (Area)", f"R {filtered_df['median_price'].median():,.0f}")
# col3.metric("Avg Solar Adoption", f"{filtered_df['solar_penetration'].mean()*100:.1f}%")

# # Chart
# st.subheader(f"Price Distribution in {muni_choice}")
# fig = px.bar(filtered_df.sort_values('median_price', ascending=False).head(15), 
#              x='suburb', y='median_price', color='resilience_score')
# st.plotly_chart(fig, width='stretch')


# ---------------------------
# 2. Market Segmentation
# ---------------------------
# st.header("Market Segmentation")
# TODO: Filter by location, property type, bedrooms
# TODO: Add tables or charts

# ---------------------------
# 3. Visual Insights
# ---------------------------
# st.header("Visual Insights")
# TODO: Distribution charts for rental price, rental yield
# TODO: Regional heatmap
# TODO: Historical trend line plots


with open("data/geo/gauteng_municipalities_clean.geojson") as f:
    gauteng_geojson = json.load(f)


# # List of municipalities and colors
# munis = ["City of Johannesburg", "City of Tshwane", "Ekurhuleni", "Sedibeng", "West Rand"]
# values = [8.2, 11.7, 10.4, 6.9, 9.6]

# df = pd.DataFrame({"municipality": munis, "muni_id": [0, 1, 2, 3, 4], "yield": values})
geo_df = filtered_sales.groupby('munis')['predicted_gross_yield'].mean().reset_index()
geo_df.columns = ['municipality', 'avg_yield']

# Plot with Plotly Express
fig = px.choropleth(
    geo_df,
    geojson=gauteng_geojson,
    locations=geo_df.index,
    featureidkey="properties.muni_id",
    color="avg_yield",
    color_continuous_scale="Viridis",
    projection='mercator',
    hover_name="municipality",
    hover_data='avg_yield'
)


fig.update_geos(
    fitbounds="locations", 
    visible=False,
    showland=False,  # This removes the default map 'sea' color
    bgcolor='rgba(0,0,0,0)' # Explicitly sets the geo area to transparent
)

fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

# Use use_container_width instead of width='stretch' for modern Streamlit
st.plotly_chart(fig)

st.subheader("Yield Efficiency Frontier")
fig_yef = px.scatter(filtered_sales, x='price', y='predicted_gross_yield', color='suburb', hover_name='suburb')
st.plotly_chart(fig_yef)


st.dataframe(filtered_sales)
st.dataframe(geo_df)

# ---------------------------
# 4. Interpretation Notes
# ---------------------------
st.subheader("Interpretation Notes")
st.write("""
- Market-level metrics are descriptive, not predictive
- High yields may correlate with higher risk
- Regional averages can mask local variation
""")
