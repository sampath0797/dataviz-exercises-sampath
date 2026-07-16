import streamlit as st
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_gapminder

df = load_gapminder()
st.header("How do countries compare today?")
st.caption("Bubble = population | Colour = continent")

years = sorted(df['year'].unique())
selected_year = st.selectbox("Year", years, index=len(years)-1)

df_y = df[df['year'] == selected_year]

c1, c2, c3 = st.columns(3)
c1.metric("Countries", len(df_y))
c2.metric("Avg Life Expectancy", f"{df_y['lifeExp'].mean():.1f}")
c3.metric("Richest country",
           df_y.loc[df_y['gdpPercap'].idxmax(), 'country'])

st.divider()

fig = px.scatter(
    df_y,
    x='gdpPercap',
    y='lifeExp',
    size='pop',
    color='continent',
    hover_name='country',
    log_x=True,
    size_max=55,
    title="Wealth vs Life Expectancy"
)

st.plotly_chart(fig, use_container_width=True)