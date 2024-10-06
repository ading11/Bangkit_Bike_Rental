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
daily_df['dteday'] = pd.to_datetime(daily_df['dteday'])
daily_df['year'] = daily_df['dteday'].dt.year
daily_df['season'] = daily_df['season'].map({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'})

# Hitung rata-rata peminjaman per tahun dan musim
avg_rentals = daily_df.groupby(['year', 'season'])[['casual', 'registered']].mean().reset_index()
avg_rentals['year_season'] = avg_rentals['year'].astype(str) + '_' + avg_rentals['season']
avg_rentals = avg_rentals.sort_values('year_season')

# Buat visualisasi
fig, ax = plt.subplots(figsize=(14, 7))
width = 0.35
x = range(len(avg_rentals))

# Plot batang
ax.bar(x, avg_rentals['casual'], width, label='Casual', color='#1f77b4')
ax.bar(x, avg_rentals['registered'], width, bottom=avg_rentals['casual'], label='Registered', color='#ff7f0e')

# Kustomisasi plot
ax.set_xlabel('Year and Season')
ax.set_ylabel('Average Number of Rentals')
ax.set_title('Seasonal and Yearly Trends: Casual vs Registered Users')
ax.set_xticks(x)
ax.set_xticklabels(avg_rentals['year_season'], rotation=45, ha='right')
ax.legend()

# Sesuaikan y-axis untuk mencocokkan gambar sebelah kanan
ax.set_ylim(0, 6000)

# Tambahkan gridlines untuk keterbacaan yang lebih baik
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()

# Tampilkan plot di Streamlit
st.pyplot(fig)

# Tambahkan penjelasan
st.write("""
Visualisasi ini menunjukkan tren musiman dan tahunan untuk pengguna casual vs terdaftar:
1. Pengguna terdaftar secara konsisten menyewa lebih banyak sepeda daripada pengguna casual di semua musim dan tahun.
2. Kedua jenis pengguna menunjukkan pola peminjaman yang lebih tinggi pada musim yang lebih hangat seperti musim panas dan musim gugur.
3. Terdapat peningkatan umum dalam peminjaman dari tahun 2011 ke 2012 untuk kedua jenis pengguna.
4. Perbedaan antara pengguna casual dan terdaftar paling terlihat pada musim puncak seperti musim panas dan musim gugur.
5. Musim dingin menunjukkan jumlah peminjaman terendah untuk kedua jenis pengguna.
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
