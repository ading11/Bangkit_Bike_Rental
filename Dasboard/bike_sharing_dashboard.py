import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Direktori data
data_dir = "Data"

# Nama file
day_file = "day.csv"
hour_file = "hour.csv"

# Load data
@st.cache_data
def load_data():
    day_data = pd.read_csv(os.path.join(data_dir, day_file))
    hour_data = pd.read_csv(os.path.join(data_dir, hour_file))
    
    # Convert date columns to datetime
    day_data['dteday'] = pd.to_datetime(day_data['dteday'])
    hour_data['dteday'] = pd.to_datetime(hour_data['dteday'])
    
    # Create weather category
    weather_map = {1: 'Clear', 2: 'Mist', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Snow'}
    day_data['weather_category'] = day_data['weathersit'].map(weather_map)
    hour_data['weather_category'] = hour_data['weathersit'].map(weather_map)
    
    return day_data, hour_data

day_data, hour_data = load_data()

# Dashboard title
st.title('Bike Sharing Dashboard')

# Sidebar
st.sidebar.header('Filters')
year = st.sidebar.selectbox('Select Year', sorted(day_data['yr'].unique() + 2011))
season = st.sidebar.multiselect('Select Season', sorted(day_data['season'].unique()), default=day_data['season'].unique())

# Filter data based on selection
filtered_day_data = day_data[(day_data['yr'] == year - 2011) & (day_data['season'].isin(season))]

# Overview metrics
st.header('Overview')
col1, col2, col3 = st.columns(3)
col1.metric("Total Rentals", f"{filtered_day_data['cnt'].sum():,}")
col2.metric("Average Daily Rentals", f"{filtered_day_data['cnt'].mean():.0f}")
col3.metric("Max Daily Rentals", f"{filtered_day_data['cnt'].max():,}")

# Daily rentals over time
st.header('Daily Rentals Over Time')
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(filtered_day_data['dteday'], filtered_day_data['cnt'])
ax.set_xlabel('Date')
ax.set_ylabel('Number of Rentals')
ax.set_title(f'Daily Bike Rentals in {year}')
st.pyplot(fig)

# Question 1: Weather impact on working days vs holidays
st.header('Question 1: Weather Impact on Working Days vs Holidays')
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='weather_category', y='cnt', hue='workingday', data=filtered_day_data,
            palette={0: 'skyblue', 1: 'orange'},
            errorbar=('ci', 95), errcolor='.2', capsize=0.1, ax=ax)
ax.set_xlabel('Weather Condition')
ax.set_ylabel('Average Number of Rentals')
ax.set_title('Weather Impact on Bike Rentals: Working Days vs Holidays')
ax.legend(title='Working Day', labels=['Holiday', 'Working Day'])
st.pyplot(fig)

st.write("""
This visualization shows how weather conditions affect bike rentals differently on working days vs holidays:
1. Bike rentals are generally higher on working days across all weather conditions.
2. Clear weather tends to have the highest number of bike rentals, followed by misty/cloudy conditions.
3. The impact of bad weather (rain/snow) is more pronounced on working days, where the number of rentals drops more significantly compared to holidays.
""")

# Question 2: Seasonal and yearly trends for casual vs registered users

# Persiapan data
st.header('Trend Musim dan Tahunan: Pada pengguna Biasa VS Terdaftar')
yearly_seasonal = day_data.groupby(['yr', 'season'])[['casual', 'registered']].mean().reset_index()
yearly_seasonal['yr'] = yearly_seasonal['yr'] + 2011  # Adjust year

fig, ax = plt.subplots(figsize=(14, 7))
width = 0.35
x = range(len(yearly_seasonal))
ax.bar([i - width/2 for i in x], yearly_seasonal['casual'], width, label='Casual')
ax.bar([i + width/2 for i in x], yearly_seasonal['registered'], width, label='Registered')

ax.set_xlabel('Year and Season')
ax.set_ylabel('Average Number of Rentals')
ax.set_title('Average Rentals by Year and Season: Casual vs Registered Users')
ax.set_xticks(x)
ax.set_xticklabels([f"{year}\n{season}" for year, season in zip(yearly_seasonal['yr'], yearly_seasonal['season'])], rotation=45)
ax.legend()
st.pyplot(fig)

st.write("""
Visualisasi ini menampilkan trend musiman dan tahunan untuk pengguna biasa vs terdaftar : 
1. Pengguna terdaftar secara konsisten menyewa lebih banyak sepeda daripada pengguna biasa di keseluruhan musim dan tahun. 
2. Kedua jenis pengguna menunjukan pola dengan penyewaan sepeda lebih tinggi pada musim yang lebih hangat seperti musim semi dan panas. 
3. Ada kenaikan umum dalam penyewaan dari tahun 2011 hingga 2012 untuk kedua jenis pengguna. 
4. Perbedaan antara pengguna biasa dan pengguna terdaftar paling menonjol di musim puncak seperti musim panas dan gugur. 
""")


# Correlation heatmap
st.header('Correlation Heatmap')
corr_columns = ['temp', 'atemp', 'hum', 'windspeed', 'casual', 'registered', 'cnt']
corr_matrix = filtered_day_data[corr_columns].corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
ax.set_title('Correlation Heatmap of Numerical Variables')
st.pyplot(fig)

st.write("""
The correlation heatmap provides insights into the relationships between different variables:
1. Temperature (temp and atemp) has a strong positive correlation with the number of rentals.
2. Humidity has a moderate negative correlation with rentals.
3. Wind speed has a weak negative correlation with rentals.
4. Registered users show a stronger correlation with total rentals (cnt) compared to casual users, indicating they contribute more to overall rental numbers.
""")

# Show raw data
if st.checkbox('Show Raw Data'):
    st.subheader('Raw Data')
    st.write(filtered_day_data)
