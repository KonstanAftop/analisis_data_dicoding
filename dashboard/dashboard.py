import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def resampling_daily(df):
    return df.resample('D').mean()

def resampling_monthly(df):
    return df.resample('MS').mean()

def seasonalcorrelation_matrices_vstemp(df):
    df = df[['CO', 'PM2.5', 'NO2', 'TEMP']]
    df = resampling_daily(df)
    
    S_MAM = df[df.index.month.isin([3,4,5])]
    S_JJA = df[df.index.month.isin([6,7,8])]
    S_SON = df[df.index.month.isin([9,10,11])]
    S_DJF = df[df.index.month.isin([12,1,2])]
    
    Corr_MAM = S_MAM.corr()['TEMP'].drop('TEMP')
    Corr_JJA = S_JJA.corr()['TEMP'].drop('TEMP')
    Corr_SON = S_SON.corr()['TEMP'].drop('TEMP')
    Corr_DJF = S_DJF.corr()['TEMP'].drop('TEMP')
    
    return Corr_DJF, Corr_JJA, Corr_MAM, Corr_SON

def classify_PM25(value):
    if value <= 25:
        return 'Good'
    elif value <= 50:
        return 'Fair'
    elif value <= 100:
        return 'Poor'
    elif value <= 300:
        return 'Very Poor'

ordered_index = ['Good', 'Fair', 'Poor', 'Very Poor']

def two_stations(df, stations):
    if len(stations) == 2:
        df1 = df[df['station'] == stations[0]]
        df2 = df[df['station'] == stations[1]]
        return [df1, df2]
    else:
        return []

df = pd.read_csv("dashboard/main_data.csv")
df.sort_values(by='date', inplace=True)
df.reset_index(drop=True, inplace=True)

df['date'] = pd.to_datetime(df['date'])
min_date = df['date'].min()
max_date = df['date'].max()

# Sidebar filters
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    start_date, end_date = st.date_input(
        label="Periode",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    selected_stations = st.multiselect(
        'Station',
        df['station'].unique(),
        default=df['station'].unique()
    )

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

main_df = df[(df['date'] >= start_date) & (df['date'] <= end_date) & df['station'].isin(selected_stations)]

st.header("Air Quality Dataset Dashboard :sparkles:")
st.subheader("PM 2.5 Summary")

# Summary Metrics
col1, col2, col3 = st.columns(3)

with col1:
    mean = main_df['PM2.5'].mean()
    st.metric('Average Concentration', value=f"{mean:.2f}")

with col2:
    minim = main_df['PM2.5'].min()
    st.metric('Minimum', value=f"{minim:.2f}")

with col3:
    maxim = main_df['PM2.5'].max()
    st.metric('Maximum', value=f"{maxim:.2f}")

# Time Series Plot
if not main_df.empty:
    main_df.set_index('date', inplace=True)

    if (end_date - start_date).days <= 100:
        df_resampled = resampling_daily(main_df[['PM2.5']])
    else:
        df_resampled = resampling_monthly(main_df[['PM2.5']])

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        df_resampled.index,
        df_resampled["PM2.5"],
        marker='o',
        linewidth=2,
        color="#90CAF9"
    )
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    
    st.pyplot(fig)
else:
    st.warning("No data available for the selected filters.")

# Seasonal Correlations
st.subheader('Pollutants Seasonal Correlations vs Temperature')

if not main_df.empty:
    Corr_DJF, Corr_JJA, Corr_MAM, Corr_SON = seasonalcorrelation_matrices_vstemp(main_df)

    fig, axes = plt.subplots(2, 2, figsize=(20, 8))
    axes = axes.flatten()
    Corr_list = [Corr_MAM, Corr_JJA, Corr_SON, Corr_DJF]
    captions = [
        "Spring Season Correlations",
        "Summer Season Correlations",
        "Autumn Season Correlations",
        "Winter Season Correlations"
    ]
    
    for i in range(4):
        sns.barplot(y=Corr_list[i].index, x=Corr_list[i].values, ax=axes[i], color='skyblue')
        axes[i].set_xlim(-1, 1)
        axes[i].set_ylabel('Pollutant')
        axes[i].axvline(0, linestyle='--', linewidth=1, color='black')
        axes[i].text(0.5, 1.05, captions[i], fontsize=10, ha='center', transform=axes[i].transAxes)

    st.pyplot(fig)

# PM2.5 Classification at Different Stations
st.subheader("PM2.5 Classification at Different Stations")

stations = two_stations(main_df, selected_stations)

if len(stations) == 2:
    fig, axes = plt.subplots(1, 2, figsize=(20, 5))
    
    for i, station in enumerate(stations):
        if not station.empty:
            value_counts = station['PM2.5'].apply(classify_PM25).value_counts()
            value_counts = value_counts.reindex(ordered_index, fill_value=0) 
            value_counts.plot(kind='barh', ax=axes[i], color='skyblue')
            axes[i].set_title(f"Station: {station['station'].iloc[0]}")
    
    st.pyplot(fig)
else:
    st.warning("Please select exactly 2 stations for comparison.")
