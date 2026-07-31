import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Global EV Charging Infrastructure",
    page_icon="⚡",
    layout="wide"
)

# --- DATA LOADING & CLEANING ---
@st.cache_data
def load_data():
    # Detect CSV file location (root vs data/ subfolder)
    file_name = 'alt_fuel_stations (Jul 29 2026).csv'
    
    if os.path.exists(file_name):
        csv_path = file_name
    elif os.path.exists(os.path.join('data', file_name)):
        csv_path = os.path.join('data', file_name)
    else:
        # Fallback search for any CSV starting with alt_fuel_stations
        possible_files = [f for f in os.listdir('.') if f.startswith('alt_fuel_stations') and f.endswith('.csv')]
        if not possible_files and os.path.exists('data'):
            possible_files = [os.path.join('data', f) for f in os.listdir('data') if f.startswith('alt_fuel_stations') and f.endswith('.csv')]
        
        if possible_files:
            csv_path = possible_files[0]
        else:
            raise FileNotFoundError(f"Could not find {file_name} in current directory or in 'data/' folder.")

    df = pd.read_csv(csv_path, low_memory=False)
    
    # Clean numeric ports
    df['EV Level2 EVSE Num'] = df['EV Level2 EVSE Num'].fillna(0)
    df['EV DC Fast Count'] = df['EV DC Fast Count'].fillna(0)
    df['Total Ports'] = df['EV Level2 EVSE Num'] + df['EV DC Fast Count']
    
    # Dates
    df['Open Date Clean'] = pd.to_datetime(df['Open Date'], errors='coerce')
    df['Year'] = df['Open Date Clean'].dt.year
    
    # Categorical clean
    df['EV Network Clean'] = df['EV Network'].fillna('Unknown / Non-Networked')
    df['Access Code'] = df['Access Code'].str.title().fillna('Public')
    df['Facility Type Clean'] = df['Facility Type'].fillna('Uncategorized')
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Global Filters")

countries = ['All'] + list(df['Country'].dropna().unique())
selected_country = st.sidebar.selectbox("Country", countries)

access_types = ['All'] + list(df['Access Code'].unique())
selected_access = st.sidebar.selectbox("Access Type", access_types)

networks = ['All'] + list(df['EV Network Clean'].value_counts().head(15).index)
selected_network = st.sidebar.selectbox("Top Network Operator", networks)

valid_years = df['Year'].dropna()
min_year = int(valid_years.min()) if not valid_years.empty else 2010
max_year = int(valid_years.max()) if not valid_years.empty else 2026

selected_years = st.sidebar.slider("Installation Year Range", 2010, 2026, (2015, 2026))

# Filter DataFrame
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
st.title("⚡ Global EV Charging Infrastructure & Adoption Dashboard")
st.markdown("Real-world tracking of EV charger deployments, charger types, power distributions, and regional adoption metrics.")

# --- KPI METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Stations", f"{len(filtered_df):,}")
col2.metric("Total Level 2 Ports", f"{int(filtered_df['EV Level2 EVSE Num'].sum()):,}")
col3.metric("Total DC Fast Ports", f"{int(filtered_df['EV DC Fast Count'].sum()):,}")
col4.metric("Avg Ports / Station", f"{filtered_df['Total Ports'].mean():.1f}" if len(filtered_df) > 0 else "0.0")

st.divider()

# --- TABS LAYOUT ---
tab1, tab2, tab3 = st.tabs(["📈 Deployment Trends", "🔌 Networks & Chargers", "🗺️ Geographic Hotspots"])

# --- TAB 1: TRENDS ---
with tab1:
    st.subheader("Temporal Deployment & Growth")
    
    if not filtered_df.empty:
        yearly_access = filtered_df.groupby(['Year', 'Access Code'])['ID'].count().reset_index()
        fig1 = px.bar(
            yearly_access, 
            x='Year', 
            y='ID', 
            color='Access Code',
            title="Public vs. Private Station Deployments Accelerated Significantly Post-2020",
            color_discrete_sequence=['#2b5c8f', '#d95f02'],
            template='plotly_white'
        )
        fig1.update_layout(xaxis_title="Year", yaxis_title="New Stations", showlegend=True)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No data available for the current filter selection.")

# --- TAB 2: NETWORKS ---
with tab2:
    st.subheader("Network Breakdown & Fast Charging")
    
    if not filtered_df.empty:
        net_summary = filtered_df.groupby('EV Network Clean')[['EV Level2 EVSE Num', 'EV DC Fast Count']].sum().reset_index()
        top_nets = net_summary.sort_values(by='EV DC Fast Count', ascending=False).head(10)
        
        fig2 = px.bar(
            top_nets, 
            x='EV Network Clean', 
            y=['EV DC Fast Count', 'EV Level2 EVSE Num'],
            title="Tesla and ChargePoint Lead Fast Charger Port Deployments",
            labels={'value': 'Total Ports', 'EV Network Clean': 'Network Operator'},
            color_discrete_sequence=['#e41a1c', '#377eb8'],
            template='plotly_white'
        )
        fig2.update_layout(barmode='stack', xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data available for the current filter selection.")

# --- TAB 3: GEOGRAPHIC MAP ---
with tab3:
    st.subheader("Spatial Station Distribution")
    
    map_data = filtered_df.dropna(subset=['Latitude', 'Longitude'])
    if not map_data.empty:
        sample_map_df = map_data.sample(min(5000, len(map_data)))
        
        fig_map = px.scatter_mapbox(
            sample_map_df,
            lat="Latitude",
            lon="Longitude",
            color="Access Code",
            size="Total Ports",
            color_discrete_sequence=['#006d2c', '#74c476'],
            hover_name="Station Name",
            hover_data=["City", "State", "EV Network Clean"],
            zoom=3,
            height=600,
            title="Geographic Concentration of EV Charging Stations"
        )
        fig_map.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No geographic location coordinates available for the current selection.")