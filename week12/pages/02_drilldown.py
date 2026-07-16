# pages/02_drilldown.py — neighbourhood drill-down page

import os
import sys

import plotly.express as px
import streamlit as st


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import load_data, sidebar_filters


df, p95 = load_data()
filtered = sidebar_filters(df, p95)


st.title("Which neighbourhoods drive the premium?")

st.caption(
    "From the market summary to one neighbourhood story"
)


hoods_available = sorted(
    filtered["neighbourhood"].dropna().unique()
)


if "sel_hood" not in st.session_state:
    st.session_state.sel_hood = hoods_available[0]
else:
    st.session_state.sel_hood = st.session_state.sel_hood


if st.session_state.sel_hood not in hoods_available:
    st.session_state.sel_hood = hoods_available[0]


st.selectbox(
    "Drill into a neighbourhood",
    hoods_available,
    key="sel_hood",
)


selected_neighbourhood = st.session_state.sel_hood

hood_df = filtered[
    filtered["neighbourhood"] == selected_neighbourhood
].copy()


k1, k2, k3 = st.columns(3)

k1.metric(
    "Listings",
    f"{len(hood_df):,}",
)

k2.metric(
    "Median Price",
    f"£{hood_df['price'].median():.0f}/night",
    f"£{hood_df['price'].median() - filtered['price'].median():+.0f} "
    "vs filtered market",
)

k3.metric(
    "Most Common Room Type",
    hood_df["room_type"].mode().iloc[0],
)


st.divider()


plot_df = filtered.copy()

plot_df["highlight"] = plot_df["neighbourhood"].apply(
    lambda neighbourhood: (
        selected_neighbourhood
        if neighbourhood == selected_neighbourhood
        else "Rest of market"
    )
)


fig = px.histogram(
    plot_df,
    x="price",
    color="highlight",
    barmode="overlay",
    histnorm="percent",
    nbins=40,
    color_discrete_map={
        selected_neighbourhood: "#2E75B6",
        "Rest of market": "#AAAAAA",
    },
    labels={
        "price": "Nightly Price (£)",
        "highlight": "",
    },
    title=f"{selected_neighbourhood} has a distinct price distribution",
)


fig.update_traces(marker_line_width=0)


fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(
        family="Arial",
        size=12,
        color="black",
    ),
    title_font=dict(
        color="black",
        size=18,
    ),
    xaxis=dict(
        title="Nightly Price (£)",
        showgrid=False,
        tickfont=dict(color="black", size=12),
        title_font=dict(color="black", size=13),
    ),
    yaxis=dict(
        title="% of listings",
        gridcolor="#EEEEEE",
        tickfont=dict(color="black", size=12),
        title_font=dict(color="black", size=13),
    ),
    legend=dict(
        orientation="h",
        y=1.08,
        font=dict(color="black"),
        title_font=dict(color="black"),
    ),
)


st.plotly_chart(fig, use_container_width=True)