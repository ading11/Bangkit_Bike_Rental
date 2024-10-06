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

# Pertanyaan Bisnis 1: Bagaimana faktor cuaca mempengaruhi jumlah peminjaman sepeda pada hari kerja vs hari libur?
st.header('Pertanyaan 1: Dampak Cuaca pada Hari Kerja VS Hari Libur')
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='weather_category', y='cnt', hue='workingday', data=filtered_day_data,
            palette={0: 'skyblue', 1: 'orange'},
            errorbar=('ci', 95), errcolor='.2', capsize=0.1)
ax.set_title('Faktor cuaca mempengaruhi jumlah peminjaman sepeda pada hari kerja vs hari libur')
ax.set_xlabel('Weather Condition')
ax.set_ylabel('Average Number of Rentals')
ax.legend(title='Working Day', labels=['Holiday', 'Working Day'])
st.pyplot(fig)

st.write("""
Insight:
- Cuaca cerah menghasilkan jumlah peminjaman tertinggi, baik pada hari kerja maupun hari libur.
- Peminjaman pada hari kerja konsisten lebih tinggi daripada hari libur di semua kondisi cuaca.
- Perbedaan jumlah peminjaman antara hari kerja dan hari libur paling signifikan pada cuaca cerah.
""")

# Pertanyaan Bisnis 2: Apakah ada pola musiman atau tren tahunan dalam peminjaman sepeda, dan bagaimana ini berbeda antara pengguna casual dan terdaftar?
st.header('Pertanyaan 2: Trend Musim dan Tahunan: Pengguna Biasa VS Terdaftar')

# Hitung rata-rata peminjaman per tahun dan musim
avg_rentals = day_data.groupby(['yr', 'season'])[['casual', 'registered']].mean().reset_index()

# Urutkan berdasarkan tahun dan musim
avg_rentals['year'] = avg_rentals['yr'] + 2011
avg_rentals['year_season'] = avg_rentals['year'].astype(str) + '_' + avg_rentals['season'].astype(str)
avg_rentals = avg_rentals.sort_values('year_season')

# Buat visualisasi
fig, ax = plt.subplots(figsize=(14, 7))
width = 0.35
x = range(len(avg_rentals))

ax.bar([i - width/2 for i in x], avg_rentals['casual'], width, label='Casual', color='#1f77b4')
ax.bar([i + width/2 for i in x], avg_rentals['registered'], width, label='Registered', color='#ff7f0e')

ax.set_xlabel('Year and Season')
ax.set_ylabel('Average Number of Rentals')
ax.set_title('Average Rentals by Year and Season: Casual vs Registered Users')
ax.set_xticks(x)
ax.set_xticklabels(avg_rentals['year_season'], rotation=45, ha='right')
ax.legend()

plt.tight_layout()
st.pyplot(fig)

st.write("""
Insight:
- Terdapat pola musiman yang jelas dalam penggunaan sepeda, dengan puncak di musim panas dan penurunan di musim dingin.
- Pengguna terdaftar menunjukkan penggunaan yang lebih tinggi dan stabil sepanjang tahun dibandingkan pengguna casual.
- Pengguna casual lebih sensitif terhadap perubahan musim, dengan peningkatan signifikan pada musim panas.
- Tren tahunan menunjukkan peningkatan jumlah peminjaman dari tahun ke tahun, terutama untuk pengguna terdaftar.
""")

# Show raw data
if st.checkbox('Show Raw Data'):
    st.subheader('Raw Data')
    st.write(filtered_day_data)
