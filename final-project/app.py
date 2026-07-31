import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    # 1. Search for potential CSV files in root directory or data/ subfolder
    possible_dirs = ['.', 'data', '../data']
    csv_file = None
    
    for d in possible_dirs:
        if os.path.exists(d):
            files = os.listdir(d)
            # Find any CSV file matching the alt_fuel naming pattern
            matches = [f for f in files if f.endswith('.csv') and 'alt_fuel' in f.lower()]
            if matches:
                csv_file = os.path.join(d, matches[0])
                break
    
    # Fallback to any .csv in the folder if specific match isn't found
    if not csv_file:
        for d in possible_dirs:
            if os.path.exists(d):
                files = os.listdir(d)
                matches = [f for f in files if f.endswith('.csv')]
                if matches:
                    csv_file = os.path.join(d, matches[0])
                    break

    if not csv_file or not os.path.exists(csv_file):
        raise FileNotFoundError(
            "No CSV file starting with 'alt_fuel' was found in your project folder! "
            "Please make sure your CSV file is placed in the same folder as app.py or in a 'data/' subfolder."
        )

    df = pd.read_csv(csv_file, low_memory=False)
    
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
