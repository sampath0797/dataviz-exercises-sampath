import streamlit as st
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_gapminder

df = load_gapminder()

st.header("How has life expectancy changed?")

with st.sidebar:
    continents = st.multiselect(
        "Continent",
        df['continent'].unique(),
        default=list(df['continent'].unique())
    )

    metric = st.radio("Metric", ["Life Expectancy", "GDP per Capita"])

if not continents:
    st.warning("Select at least one continent")
    st.stop()

col = 'lifeExp' if metric == "Life Expectancy" else 'gdpPercap'

filtered = df[df['continent'].isin(continents)]
avg = filtered.groupby(['continent', 'year'])[col].mean().reset_index()

fig = px.line(
    avg,
    x='year',
    y=col,
    color='continent',
    title=f"{metric} over time"
)

st.plotly_chart(fig, use_container_width=True)