# utils.py — shared by every page

from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    """
    Load the Airbnb London dataset and remove extreme price outliers.

    Expected dataset location:
    week12/data/airbnb_london.csv
    """

    path = Path(__file__).parent / "data" / "airbnb_london.csv"

    if not path.exists():
        st.error(
            "Dataset not found. Make sure the file exists at: "
            "week12/data/airbnb_london.csv"
        )
        st.stop()

    df = pd.read_csv(path)

    required_columns = {
        "price",
        "room_type",
        "neighbourhood",
        "reviews_per_month",
    }

    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        st.error(
            "The dataset is missing these required columns: "
            + ", ".join(sorted(missing_columns))
        )
        st.stop()

    # Remove extreme prices above the 95th percentile.
    p95 = df["price"].quantile(0.95)

    filtered_df = df[df["price"] <= p95].copy()

    return filtered_df, p95


def init_filters(df):
    """
    Initialise the shared sidebar filters once and preserve them
    when switching between pages.
    """

    min_price = int(df["price"].min())
    max_price = int(df["price"].max()) + 1

    defaults = {
        "flt_rooms": list(df["room_type"].dropna().unique()),
        "flt_hoods": sorted(df["neighbourhood"].dropna().unique()),
        "flt_price": (min_price, max_price),
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
        else:
            # Keep the filter alive across page changes.
            st.session_state[key] = st.session_state[key]


def sidebar_filters(df, p95):
    """
    Create the same persistent sidebar filters on every dashboard page.
    """

    init_filters(df)

    room_options = list(df["room_type"].dropna().unique())
    neighbourhood_options = sorted(
        df["neighbourhood"].dropna().unique()
    )

    min_price = int(df["price"].min())
    max_price = int(df["price"].max()) + 1

    with st.sidebar:
        st.header("🔎 Filters")

        st.multiselect(
            "Room type",
            room_options,
            key="flt_rooms",
        )

        st.multiselect(
            "Neighbourhood",
            neighbourhood_options,
            key="flt_hoods",
        )

        st.slider(
            "Price (£/night)",
            min_price,
            max_price,
            key="flt_price",
        )

        st.divider()

        st.caption(
            f"Prices capped at the 95th percentile (£{p95:.0f}) "
            "to remove extreme outliers."
        )

    filtered = df[
        df["room_type"].isin(st.session_state.flt_rooms)
        & df["neighbourhood"].isin(st.session_state.flt_hoods)
        & df["price"].between(*st.session_state.flt_price)
    ].copy()

    if filtered.empty:
        st.warning("No listings match the current filters.")
        st.stop()

    return filtered