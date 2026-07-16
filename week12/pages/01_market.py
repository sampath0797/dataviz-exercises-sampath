# pages/01_market.py — market summary page

import datetime
import os
import sys

import plotly.express as px
import streamlit as st


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import load_data, sidebar_filters


df, p95 = load_data()
filtered = sidebar_filters(df, p95)


st.title("What Does a London Airbnb Cost?")

st.caption(
    f"Source: Inside Airbnb | {len(filtered):,} listings shown "
    f"of {len(df):,} total"
)


k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Listings",
    f"{len(filtered):,}",
    f"{len(filtered) - len(df):+,} vs all",
)

k2.metric(
    "Median Price",
    f"£{filtered['price'].median():.0f}/night",
    f"£{filtered['price'].median() - df['price'].median():+.0f} "
    "vs overall",
)

k3.metric(
    "Avg Reviews/Month",
    f"{filtered['reviews_per_month'].mean():.1f}",
)

k4.metric(
    "Cheapest Area",
    filtered.groupby("neighbourhood")["price"].median().idxmin(),
)


st.divider()


col_left, col_right = st.columns([1.5, 1])


with col_left:
    st.subheader("The two priciest areas command a clear premium")

    med_order = (
        filtered.groupby("neighbourhood")["price"]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )

    expensive_two = med_order[:2]

    plot_df = filtered.copy()

    plot_df["highlight"] = plot_df["neighbourhood"].apply(
        lambda neighbourhood: (
            "Premium" if neighbourhood in expensive_two else "Other"
        )
    )

    # BBD HIGHLIGHT: orange for premium areas and grey for other areas.
    # BBD CVD: avoids a red-green colour combination.
    fig1 = px.box(
        plot_df,
        x="price",
        y="neighbourhood",
        color="highlight",
        color_discrete_map={
            "Premium": "#E07B39",
            "Other": "#AAAAAA",
        },
        category_orders={
            "neighbourhood": med_order,
        },
        labels={
            "price": "Nightly Price (£)",
            "neighbourhood": "",
        },
    )

    fig1.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=11),
        showlegend=False,
        xaxis=dict(gridcolor="#EEEEEE"),
        yaxis=dict(showgrid=False),
        margin=dict(l=10, r=10, t=5, b=10),
    )

    st.plotly_chart(fig1, use_container_width=True)


with col_right:
    st.subheader("Entire homes dominate the listings")

    room_counts = filtered["room_type"].value_counts().reset_index()
    room_counts.columns = ["room_type", "count"]

    # BBD CATEGORICAL COLOUR:
    # Blue, orange and grey distinguish unordered room-type categories.
    fig2 = px.bar(
        room_counts,
        x="count",
        y="room_type",
        orientation="h",
        color="room_type",
        color_discrete_map={
            "Entire home/apt": "#2E75B6",
            "Private room": "#E07B39",
            "Shared room": "#AAAAAA",
            "Hotel room": "#6B8E23",
        },
        labels={
            "count": "Listings",
            "room_type": "",
        },
    )

    fig2.update_traces(marker_line_width=0)

    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        font=dict(family="Arial", size=11),
        xaxis=dict(gridcolor="#EEEEEE"),
        yaxis=dict(showgrid=False),
        margin=dict(l=10, r=10, t=5, b=10),
    )

    st.plotly_chart(fig2, use_container_width=True)


with st.expander("📊 Show raw data sample"):
    st.dataframe(filtered.head(100), use_container_width=True)


st.divider()

st.caption(
    f"Inside Airbnb | Prices capped at the 95th percentile "
    f"(£{p95:.0f}) | Last shown: {datetime.date.today()}"
)