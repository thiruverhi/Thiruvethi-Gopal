import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

sns.set_style("whitegrid")

# -----------------------------
# Title
# -----------------------------
st.markdown(
    "<h1 style='text-align: center;'>🚲 Bike Sharing Interactive Dashboard</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center;'>Exploring how time and weather affect bike rentals</p>",
    unsafe_allow_html=True
)
st.divider()

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv("traindataset.csv")
df["datetime"] = pd.to_datetime(df["datetime"])

# -----------------------------
# Feature engineering
# -----------------------------
df["year"] = df["datetime"].dt.year
df["month"] = df["datetime"].dt.month
df["hour"] = df["datetime"].dt.hour
df["day_of_week"] = df["datetime"].dt.day_name()

df["total_count"] = df["casual"] + df["registered"]

season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
weather_map = {1: "Clear", 2: "Mist", 3: "Light Snow/Rain", 4: "Heavy Rain"}

df["season_name"] = df["season"].map(season_map)
df["weather_name"] = df["weather"].map(weather_map)

def day_period(hour):
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"

df["day_period"] = df["hour"].apply(day_period)

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("🎛 Filters")

year_filter = st.sidebar.multiselect(
    "Select Year",
    sorted(df["year"].unique()),
    default=sorted(df["year"].unique())
)

season_filter = st.sidebar.multiselect(
    "Select Season",
    df["season_name"].unique(),
    default=df["season_name"].unique()
)

hour_filter = st.sidebar.slider(
    "Hour Range",
    0, 23, (0, 23)
)

filtered_df = df[
    (df["year"].isin(year_filter)) &
    (df["season_name"].isin(season_filter)) &
    (df["hour"] >= hour_filter[0]) &
    (df["hour"] <= hour_filter[1])
]

# -----------------------------
# KPI Cards
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Rentals", f"{filtered_df['total_count'].sum():,}")
col2.metric("Average Hourly Rentals", int(filtered_df["total_count"].mean()))
col3.metric("Peak Hour", filtered_df.groupby("hour")["total_count"].mean().idxmax())

st.divider()

# -----------------------------
# Charts Row 1
# -----------------------------
col4, col5 = st.columns(2)

with col4:
    st.subheader("📈 Average Rentals by Hour")
    fig, ax = plt.subplots()
    filtered_df.groupby("hour")["total_count"].mean().plot(ax=ax, color="#1f77b4")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Average Rentals")
    st.pyplot(fig)

with col5:
    st.subheader("🍩 Rentals Share by Season")
    season_data = filtered_df.groupby("season_name")["total_count"].sum()
    fig, ax = plt.subplots()
    ax.pie(
        season_data,
        labels=season_data.index,
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"width": 0.4}
    )
    ax.axis("equal")
    st.pyplot(fig)

# -----------------------------
# Charts Row 2
# -----------------------------
col6, col7 = st.columns(2)

with col6:
    st.subheader("🌦 Average Rentals by Weather")
    fig, ax = plt.subplots()
    sns.barplot(
        x="weather_name",
        y="total_count",
        data=filtered_df,
        errorbar=("ci", 95),
        ax=ax
    )
    ax.set_xlabel("Weather")
    ax.set_ylabel("Average Rentals")
    st.pyplot(fig)

with col7:
    st.subheader("🕒 Rentals by Day Period")
    fig, ax = plt.subplots()
    filtered_df.groupby("day_period")["total_count"].mean().plot(
        kind="bar", ax=ax, color="#ff7f0e"
    )
    ax.set_xlabel("Day Period")
    ax.set_ylabel("Average Rentals")
    st.pyplot(fig)

# -----------------------------
# Heatmap
# -----------------------------
st.subheader("🔥 Hour vs Day Heatmap")
pivot = filtered_df.pivot_table(
    values="total_count",
    index="day_of_week",
    columns="hour",
    aggfunc="mean"
)

fig, ax = plt.subplots(figsize=(12, 4))
sns.heatmap(pivot, cmap="YlOrRd", ax=ax)
st.pyplot(fig)

st.success("Dashboard updated with enhanced visuals and interactivity ✅")