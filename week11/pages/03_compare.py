import streamlit as st
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_gapminder

df = load_gapminder()
latest = df[df['year'] == df['year'].max()]

st.header("What explains the differences?")

if 'country' not in st.session_state:
    st.session_state.country = 'India'

countries = sorted(latest['country'].unique())

st.session_state.country = st.selectbox(
    "Select country",
    countries,
    index=countries.index(st.session_state.country)
)

country = st.session_state.country

tab1, tab2 = st.tabs(["GDP vs Life Expectancy", "Life Expectancy Ranking"])

with tab1:
    fig = px.scatter(
        latest,
        x='gdpPercap',
        y='lifeExp',
        color='continent',
        hover_name='country',
        log_x=True
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    df_ct = latest[latest['continent'] == latest[latest['country'] == country]['continent'].values[0]]
    df_ct = df_ct.sort_values('lifeExp')

    fig = px.bar(
        df_ct,
        x='lifeExp',
        y='country',
        orientation='h',
        title=f"{country} vs peers"
    )

    st.plotly_chart(fig, use_container_width=True)