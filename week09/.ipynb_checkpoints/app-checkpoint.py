import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config for a wide dashboard layout (Big Book of Dashboards standard)
st.set_page_config(page_title="World Happiness", page_icon="🌍", layout="wide")

# ── DATA LOADING ─────────────────────────────────────────────────────────────
# Safely handles file paths across both local laptop running and Streamlit Cloud environments
try:
    df = pd.read_csv('week09/world_happiness_2023.csv') # Inside week09 folder (Streamlit Cloud structure)
except FileNotFoundError:
    try:
        df = pd.read_csv('world_happiness_2023.csv') # Root folder location (Local script execution)
    except FileNotFoundError:
        try:
            df = pd.read_csv('../data/world_happiness_2023.csv') # Lecture notes default path
        except FileNotFoundError:
            df = pd.read_csv('data/world_happiness_2023.csv')

# Standardize columns for clean coding
df.columns = ['Country','Region','Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']

# Calculate global average score to serve as the meaningful midpoint for Step 6
global_avg_score = df['Score'].mean()

# ── SIDEBAR FILTERS ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    regions = ['All'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N countries", 5, 25, 15)

# Filter dataset reactively based on user inputs
filtered = df if selected_region == 'All' else df[df['Region'] == selected_region]

# ── DASHBOARD HEADER & KPIs ──────────────────────────────────────────────────
st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# KPI row — BBD Principle: Large numbers at the top, readable within 5 seconds
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric(
    "Avg Score", 
    f"{filtered['Score'].mean():.2f}",
    f"{filtered['Score'].mean() - global_avg_score:+.2f} vs global"
)
col3.metric("Happiest Country", filtered.nlargest(1,'Score')['Country'].values[0])

st.divider()

# ── ROW 1: TWO-COLUMN LAYOUT ─────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Rankings")
    top = filtered.nlargest(top_n, 'Score').sort_values('Score')
    
    # Ordered bars — sequential tracking
    fig1 = px.bar(top, x='Score', y='Country', orientation='h',
                  color_discrete_sequence=['#2E75B6'],
                  labels={'Score':'Score (0–10)','Country':''})
    
    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       xaxis=dict(range=[0,8.5], gridcolor='#EEEEEE'), 
                       font=dict(family='Arial',size=12),
                       margin=dict(l=10,r=10,t=5,b=10))
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("Score vs GDP")
    
    # Scatter plot tracking structural correlation
    fig2 = px.scatter(filtered, x='GDP', y='Score', hover_name='Country',
                      color_discrete_sequence=['#E63946'])
    
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       xaxis=dict(gridcolor='#EEEEEE'),
                       yaxis=dict(gridcolor='#EEEEEE'),
                       font=dict(family='Arial',size=12),
                       margin=dict(l=10,r=10,t=5,b=10))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── ROW 2: STEP 6 - REQUIRED DIVERGING COLOUR SCALE CHART ───────────────────
st.subheader("Deviation from Global Average Happiness Score")
st.markdown(
    f"This visualization highlights countries scoring above or below the **Global Average Score ({global_avg_score:.2f})**."
)

# Deep copy filtered data and calculate variation from the baseline midpoint
filtered_dev = filtered.copy()
filtered_dev['Deviation'] = filtered_dev['Score'] - global_avg_score
div_data = filtered_dev.sort_values('Deviation')

# Build diverging horizontal bar chart using a Red-Blue ('RdBu') preattentive scale
fig3 = px.bar(
    div_data, 
    x='Deviation', 
    y='Country', 
    orientation='h',
    color='Deviation',
    color_continuous_scale='RdBu',   # True diverging scale
    color_continuous_midpoint=0,     # Strict midpoint setting at 0 variance
    labels={'Deviation': 'Difference from Global Avg', 'Country': ''}
)

# Layout presentation fine-tuning
fig3.update_layout(
    plot_bgcolor='white', 
    paper_bgcolor='white',
    height=550,
    font=dict(family='Arial', size=12),
    coloraxis_showscale=True
)
fig3.update_traces(marker_line_width=0)

# Reference Annotation Line matching professor instructions
fig3.add_vline(x=0, line_dash="dash", line_color="#555555", line_width=1.5)

# Clear annotation labeling the calculated global baseline midpoint (FIXED: HTML tags used for boldness)
fig3.add_annotation(
    x=0, y=1,
    text=f"<b>Global Avg Baseline ({global_avg_score:.2f})</b>",
    showarrow=False,
    xref="x", yref="paper",
    yshift=12,
    font=dict(color="#555555", size=11)
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.caption("Built with Streamlit + Plotly | Data Visualization Foundations")