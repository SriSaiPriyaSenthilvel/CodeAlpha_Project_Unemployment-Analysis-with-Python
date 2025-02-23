import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile

# Function to load data
def load_data():
    zip_path = os.path.join(os.getcwd(), "archive (3).zip")
    csv_filename = "Unemployment_Rate_upto_11_2020.csv"
    
    if not os.path.exists(zip_path):
        st.error(f"File not found: {zip_path}. Please check the file path.")
        return None
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        if csv_filename not in z.namelist():
            st.error(f"CSV file '{csv_filename}' not found in the ZIP archive.")
            return None
        
        with z.open(csv_filename) as file:
            df = pd.read_csv(file, encoding='utf-8')
    
    # Strip spaces from column names & values
    df.columns = df.columns.str.strip()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Ensure correct column names
    expected_columns = ['Date', 'Region', 'Estimated Unemployment Rate (%)']
    df.columns = [col.strip() for col in df.columns]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Missing expected columns: {missing_columns}. Check your dataset.")
        return None
    
    # Convert Date column to datetime
    df["Date"] = pd.to_datetime(df["Date"].astype(str).str.strip(), format="%d-%m-%Y", dayfirst=True, errors='coerce')
    df.dropna(subset=["Date"], inplace=True)  # Drop rows with invalid dates
    
    # Ensure 'Estimated Unemployment Rate (%)' is numeric
    df["Estimated Unemployment Rate (%)"] = pd.to_numeric(df["Estimated Unemployment Rate (%)"], errors='coerce')
    df.dropna(subset=["Estimated Unemployment Rate (%)"], inplace=True)
    
    return df

# Streamlit UI
st.set_page_config(page_title="Unemployment Rate Analysis", layout="wide")
st.title("📊 Unemployment Rate Analysis")

# Load Data
df = load_data()
if df is not None:
    # Show raw data
    st.sidebar.header("🔍 Filters")
    regions = df['Region'].dropna().unique().tolist()
    selected_region = st.sidebar.selectbox("Select Region", ["All"] + regions)
    
    if selected_region != "All":
        df = df[df['Region'] == selected_region]
    
    st.subheader("📝 Raw Data Preview")
    st.dataframe(df.head())
    
    # Summary Metrics
    st.subheader("📈 Unemployment Statistics")
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Mean Unemployment Rate", f"{df['Estimated Unemployment Rate (%)'].mean():.2f}%")
        col2.metric("Max Unemployment Rate", f"{df['Estimated Unemployment Rate (%)'].max():.2f}%")
        col3.metric("Min Unemployment Rate", f"{df['Estimated Unemployment Rate (%)'].min():.2f}%")
    else:
        st.warning("No data available for the selected region.")
    
    # Visualization
    st.subheader("📉 Unemployment Trend")
    if not df.empty:
        fig, ax = plt.subplots(figsize=(12,6))
        sns.lineplot(data=df, x="Date", y="Estimated Unemployment Rate (%)", marker="o", ax=ax, color='blue')
        ax.set_xlabel("Date")
        ax.set_ylabel("Unemployment Rate (%)")
        ax.set_title("Unemployment Rate Over Time", fontsize=14, fontweight='bold')
        plt.xticks(rotation=45)
        plt.grid(True)
        st.pyplot(fig)
        
        st.subheader("📊 Data Distribution")
        fig, ax = plt.subplots(figsize=(8,5))
        sns.histplot(df["Estimated Unemployment Rate (%)"], bins=10, kde=True, ax=ax, color='green')
        ax.set_xlabel("Unemployment Rate (%)")
        ax.set_title("Distribution of Unemployment Rate", fontsize=14, fontweight='bold')
        plt.grid(True)
        st.pyplot(fig)
    
    # Show DataFrame
    st.subheader("📋 Filtered Data")
    st.dataframe(df)
