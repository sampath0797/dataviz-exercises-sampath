import plotly.express as px
import streamlit as st

@st.cache_data
def load_gapminder():
    return px.data.gapminder()