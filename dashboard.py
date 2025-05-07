import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# Automatically select today's master DB file
today_date = datetime.datetime.now().strftime("%Y_%m_%d")
DB_PATH = fr"D:\CoolDrinkDetection\RestrictedDB\master_{today_date}.db"


def load_data():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT brand, detection_status, timestamp FROM detections ORDER BY timestamp DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    df["timestamp"] = pd.to_datetime(df["timestamp"])  # Convert timestamp to datetime
    return df



# Load Data
df = load_data()

# Streamlit Dashboard UI
st.title("📊 Cool Drink Detection - Advanced Analytics Dashboard")

# 1️⃣ **Display Total Brand Count Across All Shifts**
st.subheader("📈 Detection Analysis by Brand (Total Count Across All Shifts)")
if df.empty:
    st.warning("No detection data found!")
else:
    brand_counts = df["brand"].value_counts().reset_index()
    brand_counts.columns = ["Brand", "Total Detections"]
    
    # Display the total count as a table
    st.dataframe(brand_counts)

    # Brand-wise bar chart
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x="Brand", y="Total Detections", data=brand_counts, ax=ax, palette="coolwarm")
    ax.set_title("Total Detections Per Brand")
    plt.xticks(rotation=30)
    st.pyplot(fig)

# 2️⃣ **Shift-wise Detection Trends (Brand Count in Each Shift)**
st.subheader("📅 Shift-wise Detection Trends")

# Function to categorize shifts
def categorize_shift(hour):
    if 6 <= hour < 14:
        return "Shift 1 (6 AM - 2 PM)"
    elif 14 <= hour < 22:
        return "Shift 2 (2 PM - 10 PM)"
    else:
        return "Shift 3 (10 PM - 6 AM)"

# Apply shift categorization
df["shift"] = df["timestamp"].dt.hour.apply(categorize_shift)

# Shift selection dropdown
selected_shift = st.selectbox("Select Shift", ["All", "Shift 1 (6 AM - 2 PM)", "Shift 2 (2 PM - 10 PM)", "Shift 3 (10 PM - 6 AM)"])

# Filter based on selected shift
if selected_shift != "All":
    shift_filtered_df = df[df["shift"] == selected_shift]
else:
    shift_filtered_df = df

if shift_filtered_df.empty:
    st.warning("No data available for this shift!")
else:
    shift_brand_counts = shift_filtered_df["brand"].value_counts().reset_index()
    shift_brand_counts.columns = ["Brand", "Detections in Selected Shift"]

    # Display the shift-wise count as a table
    st.dataframe(shift_brand_counts)

    # Shift-wise bar chart
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x="Brand", y="Detections in Selected Shift", data=shift_brand_counts, ax=ax, palette="viridis")
    ax.set_title(f"Detections Per Brand in {selected_shift}")
    plt.xticks(rotation=30)
    st.pyplot(fig)
