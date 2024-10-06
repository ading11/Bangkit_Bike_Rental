import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# [Previous data loading and preprocessing code remains the same]

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
st.header('Question 2: Seasonal and Yearly Trends: Casual vs Registered Users')
yearly_seasonal = day_data.groupby(['yr', 'season'])[['casual', 'registered']].mean().reset_index()
yearly_seasonal['yr'] = yearly_seasonal['yr'] + 2011  # Adjust year

fig, ax = plt.subplots(figsize=(14, 7))
width = 0.35
x = range(len(yearly_seasonal))
ax.bar([i - width/2 for i in x], yearly_seasonal['casual'], width, label='Casual', color='#1f77b4')
ax.bar([i + width/2 for i in x], yearly_seasonal['registered'], width, label='Registered', color='#ff7f0e')

ax.set_xlabel('Year and Season')
ax.set_ylabel('Average Number of Rentals')
ax.set_title('Seasonal and Yearly Trends: Casual vs Registered Users')
ax.set_xticks(x)
ax.set_xticklabels([f"{year}\n{season}" for year, season in zip(yearly_seasonal['yr'], yearly_seasonal['season'])], rotation=45)
ax.legend()
st.pyplot(fig)

st.write("""
This visualization shows the seasonal and yearly trends for casual vs registered users:
1. Registered users consistently rent more bikes than casual users across all seasons and years.
2. Both types of users show a pattern of higher rentals in warmer seasons like spring and summer.
3. There's a general increase in rentals from 2011 to 2012 for both types of users.
4. The difference between casual and registered users is most pronounced in peak seasons like summer and fall.
""")

# Additional Analysis: Rentals by Day of Week
st.header('Additional Analysis: Rentals by Day of Week')
fig, ax = plt.subplots(figsize=(12, 6))
day_data.groupby('weekday')[['casual', 'registered']].mean().plot(kind='bar', ax=ax)
ax.set_title('Average Rentals by Day of Week')
ax.set_xlabel('Day of Week (0 = Sunday, 6 = Saturday)')
ax.set_ylabel('Average Number of Rentals')
ax.legend(['Casual', 'Registered'])
st.pyplot(fig)

st.write("""
This visualization shows the average rentals by day of the week for casual and registered users:
1. Registered users show higher rental numbers on weekdays (1-5), with a drop on weekends.
2. Casual users have higher rental numbers on weekends (0 and 6) compared to weekdays.
3. This pattern suggests that registered users might be using bikes for commuting, while casual users are more likely to rent for leisure on weekends.
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
