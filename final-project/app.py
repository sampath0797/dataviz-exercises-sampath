import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Global EV Charging Infrastructure",
    page_icon="⚡",
    layout="wide"
)

# --- DATA LOADING (Direct from URL) ---
@st.cache_data
def load_data():
    # Direct link to public official NREL Alternative Fuel Stations dataset
    url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2022/2022-03-01/stations.csv"
    
    # Read CSV directly from web
    raw_df = pd.read_csv(url, low_memory=False)
    
    # Filter for Electric Vehicle (EV) stations only
    df = raw_df[raw_df['FUEL_TYPE_CODE'] == 'ELEC'].copy()
    
    # Standardize column names to match dashboard expectations
    df['ID'] = df['ID']
    df['Station Name'] = df['STATION_NAME']
    df['Country'] = df['COUNTRY'].fillna('US')
    df['State'] = df['STATE']
    df['Latitude'] = pd.to_numeric(df['LATITUDE'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
    
    # Ports & Metrics
    df['EV Level2 EVSE Num'] = pd.to_numeric(df['EV_LEVEL2_EVSE_NUM'], errors='coerce').fillna(0)
    df['EV DC Fast Count'] = pd.to_numeric(df['EV_DC_FAST_COUNT'], errors='coerce').fillna(0)
    df['Total Ports'] = df['EV Level2 EVSE Num'] + df['EV DC Fast Count']
    
    # Dates & Categories
    df['Open Date Clean'] = pd.to_datetime(df['OPEN_DATE'], errors='coerce')
    df['Year'] = df['Open Date Clean'].dt.year
    df['EV Network Clean'] = df['EV_NETWORK'].fillna('Unknown / Non-Networked')
    df['Access Code'] = df['GROUPS_WITH_ACCESS_CODE'].astype(str).str.title().fillna('Public')
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error fetching data directly from web source: {e}")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Global Filters")

countries = ['All'] + sorted(list(df['Country'].dropna().unique()))
selected_country = st.sidebar.selectbox("Country", countries)

access_types = ['All'] + list(df['Access Code'].unique())
selected_access = st.sidebar.selectbox("Access Type", access_types)

networks = ['All'] + list(df['EV Network Clean'].value_counts().head(15).index)
selected_network = st.sidebar.selectbox("Top Network Operator", networks)

valid_years = df['Year'].dropna()
min_yr = int(valid_years.min()) if not valid_years.empty else 2010
max_yr = int(valid_years.max()) if not valid_years.empty else 2026

selected_years = st.sidebar.slider("Installation Year Range", 2010, 2026, (2012, 2022))

# Apply Filters
filtered_df = df.copy()
if selected_country != 'All':
    filtered_df = filtered_df[filtered_df['Country'] == selected_country]
if selected_access != 'All':
    filtered_df = filtered_df[filtered_df['Access Code'] == selected_access]
if selected_network != 'All':
    filtered_df = filtered_df[filtered_df['EV Network Clean'] == selected_network]

filtered_df = filtered_df[
    (filtered_df['Year'] >= selected_years[0]) & 
    (filtered_df['Year'] <= selected_years[1])
]

# --- HEADER SECTION ---
st.title("⚡ Global EV Charging Infrastructure Dashboard")
st.markdown("Real-world tracking of EV charger deployments, charger types, power distributions, and regional metrics.")

# --- KPI METRICS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Stations", f"{len(filtered_df):,}")
c2.metric("Level 2 Ports", f"{int(filtered_df['EV Level2 EVSE Num'].sum()):,}")
c3.metric("DC Fast Ports", f"{int(filtered_df['EV DC Fast Count'].sum()):,}")
c4.metric("Avg Ports / Station", f"{filtered_df['Total Ports'].mean():.1f}" if len(filtered_df) > 0 else "0.0")

st.divider()

# --- TABS LAYOUT ---
t1, t2, t3 = st.tabs(["📈 Deployment Trends", "🔌 Networks & Chargers", "🗺️ Geographic Hotspots"])

with t1:
    st.subheader("Temporal Deployment & Growth")
    if not filtered_df.empty:
        yearly_access = filtered_df.groupby(['Year', 'Access Code'])['ID'].count().reset_index()
        fig1 = px.bar(
            yearly_access, x='Year', y='ID', color='Access Code',
            title="Public vs. Private Station Deployments Accelerated Significantly Over Time",
            color_discrete_sequence=['#2b5c8f', '#d95f02'],
            template='plotly_white'
        )
        st.plotly_chart(fig1, use_container_width=True)

with t2:
    st.subheader("Network Breakdown & Fast Charging")
    if not filtered_df.empty:
        net_summary = filtered_df.groupby('EV Network Clean')[['EV Level2 EVSE Num', 'EV DC Fast Count']].sum().reset_index()
        top_nets = net_summary.sort_values(by='EV DC Fast Count', ascending=False).head(10)
        fig2 = px.bar(
            top_nets, x='EV Network Clean', y=['EV DC Fast Count', 'EV Level2 EVSE Num'],
            title="Top Operators by Fast Charging vs Level 2 Port Volume",
            labels={'value': 'Total Ports', 'EV Network Clean': 'Network Operator'},
            color_discrete_sequence=['#e41a1c', '#377eb8'],
            template='plotly_white'
        )
        st.plotly_chart(fig2, use_container_width=True)

with t3:
    st.subheader("Spatial Station Distribution")
    map_data = filtered_df.dropna(subset=['Latitude', 'Longitude'])
    if not map_data.empty:
        sample_map_df = map_data.sample(min(5000, len(map_data)))
        fig_map = px.scatter_mapbox(
            sample_map_df, lat="Latitude", lon="Longitude", color="Access Code",
            size="Total Ports", color_discrete_sequence=['#006d2c', '#74c476'],
            hover_name="Station Name", zoom=3, height=600,
            title="Geographic Concentration of EV Charging Stations"
        )
        fig_map.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig_map, use_container_width=True)