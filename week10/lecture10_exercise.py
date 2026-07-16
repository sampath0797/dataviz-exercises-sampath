import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import datetime

# --------------------------------------------------
# Load Data
# --------------------------------------------------

@st.cache_data
def load_data():
    path = Path(__file__).parent / "data" / "co2_emissions.csv"
    df = pd.read_csv(path)

    # Create Date column from Year
    df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-01-01")

    return df


df = load_data()

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("CO₂ Emissions Dashboard")

# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------

with st.sidebar:
    st.header("Filters")

    # Region Filter
    regions = ["All"] + sorted(df["Region"].unique())
    selected_region = st.selectbox("Region", regions)

    # Chained Country Filter
    if selected_region == "All":
        country_options = sorted(df["Country"].unique())
    else:
        country_options = sorted(
            df[df["Region"] == selected_region]["Country"].unique()
        )

    selected_countries = st.multiselect(
        "Countries",
        options=country_options,
        default=country_options[:3]
    )

    # Year Range Slider
    year_range = st.slider(
        "Year Range",
        int(df["Year"].min()),
        int(df["Year"].max()),
        (2000, 2022)
    )

    # Date Range Input
    date_range = st.date_input(
        "Date Range",
        value=(
            datetime.date(2005, 1, 1),
            datetime.date(2020, 1, 1)
        ),
        min_value=datetime.date(
            int(df["Year"].min()), 1, 1
        ),
        max_value=datetime.date(
            int(df["Year"].max()), 1, 1
        )
    )

    # Metric Radio Button
    metric = st.radio(
        "Metric",
        ["Total CO2 (Mt)", "CO2 per capita"]
    )

# --------------------------------------------------
# Validation
# --------------------------------------------------

if not selected_countries:
    st.warning("Select at least one country.")
    st.stop()

if len(date_range) != 2:
    st.warning("Please select both a start and end date.")
    st.stop()

# --------------------------------------------------
# Convert Dates
# --------------------------------------------------

start_ts = pd.Timestamp(date_range[0])
end_ts = pd.Timestamp(date_range[1])

# --------------------------------------------------
# Filtering
# --------------------------------------------------

filtered = df[
    (df["Country"].isin(selected_countries))
    & (df["Year"] >= year_range[0])
    & (df["Year"] <= year_range[1])
    & (df["Date"] >= start_ts)
    & (df["Date"] <= end_ts)
]

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# --------------------------------------------------
# Metric Selection
# --------------------------------------------------

if metric == "Total CO2 (Mt)":
    y_col = "CO2_Mt"
    y_label = "CO₂ Emissions (Mt)"
else:
    y_col = "CO2_per_capita"
    y_label = "CO₂ Per Capita"

# --------------------------------------------------
# Filter Summary
# --------------------------------------------------

st.caption(
    f"Showing {len(filtered)} records | "
    f"{len(selected_countries)} countries | "
    f"{selected_region} | "
    f"{year_range[0]} - {year_range[1]} | "
    f"{metric}"
)

# --------------------------------------------------
# Charts
# --------------------------------------------------

col1, col2 = st.columns(2)

# Line Chart
with col1:
    fig1 = px.line(
        filtered,
        x="Year",
        y=y_col,
        color="Country",
        labels={y_col: y_label},
        title=f"{metric} Over Time"
    )

    fig1.update_layout(
        template="plotly_dark",
        font=dict(size=14)
    )

    st.plotly_chart(fig1, use_container_width=True)

# Bar Chart
with col2:
    latest_year = filtered["Year"].max()

    latest = (
        filtered[filtered["Year"] == latest_year]
        .sort_values(y_col)
    )

    fig2 = px.bar(
        latest,
        x=y_col,
        y="Country",
        orientation="h",
        title=f"Ranking ({latest_year})"
    )

    fig2.update_layout(
        template="plotly_dark",
        font=dict(size=14)
    )

    st.plotly_chart(fig2, use_container_width=True)