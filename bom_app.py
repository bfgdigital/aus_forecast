
# Web App
import streamlit as st

# Maths and Dataframes
import pandas as pd

# Time Functions
import datetime as dt

# API fetching
import requests

# Charting
from matplotlib import pyplot as plt
import seaborn as sns



# App Begins
st.write("""
# BOM Weather

#### A project evaluating the Persistence Model against the AUS Bureau of Meteorology.
We often get a 7 day weather forecast but don't often go back to see how accurate the predictions were for 7 days ago.   
This project looks to explore how accurate the weather forecast is according to a what is known as the Persistence Model.
The Persistence Model hypothesis for the weather domain is that "The weather tomorrow will be the same as today",   
or in mathematical terms Weather(t+1) = Weather(t), (t being today, or chosen point in time).

The BOM forecasts are known to be very accurate for t = 1,2 and 3 days into the future, so this project will evaluate the whole 7 day forecast.

The persistence model, also called the naïve predictor, is often used as a reference as it is a good ground estimation of other algorithms,and often used as a reference for determining the skill factor of a competing forecast model.   

The second part of this project will try to predict the weather, using the persistence model as a feature, giving some adjustment to standard forcasting models Facebook prophet and Random Forrest trained on historical data.

All data is available for free via the BOM website and examples are stored in the repository.
 
[Click here for EDA notebook GitHub](https://github.com/bfgdigital/BOM_Weather/blob/main/notebooks/eda.ipynb)
""")

st.text('Establish a date for today')

# Define Times
today = dt.date.today()
todaystr = today.strftime("%Y-%m-%d")

yesterday = dt.date.today() - pd.DateOffset(days=1)
yesterdaystr = yesterday.strftime("%Y-%m-%d")

tomorrow = dt.date.today() + pd.DateOffset(days=1)
tomorrowstr = tomorrow.strftime("%Y-%m-%d")

day_after_tomorrow = dt.date.today() + pd.DateOffset(days=2)
day_after_tomorrowstr = day_after_tomorrow.strftime("%Y-%m-%d")

st.text(f'Yesterdays\'s date was: {yesterday.date()}')
st.text(f'Today\'s date is: {today}')
st.text(f'Tomorrows\'s date is: {tomorrow.date()}')
st.text(f'Day after that is: {day_after_tomorrow.date()}')

st.write("""
#### DATA Sources 
- Data Comes From: ftp://ftp.bom.gov.au/anon/gen/fwo/
- Melbourne Forecast File: ftp://ftp.bom.gov.au/anon/gen/fwo/IDV10450.xml

The url for the BOM API is:
https://api.weather.bom.gov.au/v1/locations/r1r143/forecasts/daily   
Be Aware that the update is adjusted every 10mins.
""")

# Forecast Locations
locations = {
'Melbourne' : 'https://api.weather.bom.gov.au/v1/locations/r1r143/forecasts/daily',
} # Melbourne last so it will be used for this iteration of the project.

# Fetch Locations with requests.
for name,url in locations.items():
    response = requests.get(url)
    weather_dict = response.json() # format as json
    latest_forecast = weather_dict
    api_forecast = pd.DataFrame(latest_forecast['data'])
    api_forecast.index=api_forecast['date']
#     filename = '../data/forecast_records/forecast_' + str(name) + '_' + todaystr + '.csv'
#     api_forecast.to_csv(filename) # backup file.


st.write("""
#### Summary of New Forecasts
""")

# Define Issue Time
issue_time = pd.to_datetime(latest_forecast['metadata']['issue_time']).date()
st.text(f'Forecast was issued on: {issue_time}')

# Check Forecast Status
forecast_status = 0
if issue_time == today:
    st.text('API forecast row 0 is for tomorrow')
    forecast_status = 1
elif issue_time == yesterday:
    st.text('API forecast row 0 is for today')
else:
    st.text('Check API data.')
    forecast_status = 2
    
# Fix Dates
lf = pd.DataFrame(latest_forecast['data'])
lf['date'] = pd.to_datetime(lf['date']).dt.date

if forecast_status == 1: # We want to bump the date column forwards 1 day.
    lf[['date']] = lf[['date']] + pd.DateOffset(days=1) # add 1 day
    st.text(f"Forecast date index moved forwards 1 day.")
else:
    forecast_status == 0 # We want to bump the date column forwards 1 day.
    st.text(f"Dates are correct, no need to change index")

# Set Date as Index
lf.index = lf['date']
st.text(f"Todays Max: {lf.index[0]} {list(lf['temp_max'][:1])}, Forecasts: {list(lf['temp_max'][1:])}")

class color:
   BOLD = '\033[1m'
   END = '\033[0m'

# Summary
number_of_forecasts = len(latest_forecast['data'])
st.text(f"New forecasts:	{number_of_forecasts}")
st.text(f"Starting on:	{lf['date'][0]}")
st.text(f"Ending on:	{lf['date'][-1]}")
st.text(f"Today's Temp:		{lf['temp_max'][0]}")
st.text(f"Tomorrow's Temp:	{lf['temp_max'][1]}\n")
st.text(color.BOLD + f"Here's today's forecast: \n{lf['extended_text'][0]}" + color.END)

# Load previous File.
temps = pd.read_csv('./data/temps.csv',infer_datetime_format=True,index_col=0)

# Remove other locations for the moment
temps = temps[temps['location'] == 'Melbourne'].drop(['location'], axis=1)

# Display Previous Data
st.write("""
#### Previous Forecasts
# """)
st.dataframe(temps)

# Heatmap Function
def heat_map(data,title):
    fig, ax = plt.subplots(figsize = (10,10))
    ax = sns.heatmap(data, annot=True, center=True, cmap = 'coolwarm',cbar_kws={'label': 'Degrees Celcius'})
    ax.set_title(title, loc='center', fontsize=18)
    ax.set_xticklabels(ax.xaxis.get_ticklabels(), fontsize=14, rotation=30)
    ax.set_yticklabels(ax.yaxis.get_ticklabels(), fontsize=14, rotation=0)
    ax.figure.axes[-1].yaxis.label.set_size(14)
    ax.figure.axes[0].yaxis.label.set_size(14)
    ax.figure.axes[0].xaxis.label.set_size(14)
    # return plt.show();
    return st.pyplot(fig);

# Display Heatmap
st.write("""
#### Heatmap of Forecasts   
""")
heat_map(temps,"7 Day Forecasts From BOM (Decending to the left)")


st.write("""
# Evaluate Accuracy
Shown are the BOM Forecast accuracy.
""")

basic_dates = temps.index # Keep non-datetime index list for charts. (avoid 00:00:00 ending)
temps.index = pd.to_datetime(temps.index) # make index a datetime.

# Acuracy Mechanism: Compare forecast to actual Temp.
fac = pd.DataFrame()
counter = list(range(len(temps)))
columns = list(temps.columns)

for i in counter:
    # 7 day forecast inc today, so len can't exceed 7
    if i < 7:
        window = i 
        j = i
    else: 
        window = 6
        j = 6
    
    # Start date at most recent row
    actual_date = temps.index[-1] # start with the last day
    window_date = actual_date - pd.DateOffset(days=window) # Number of days in the past can't be more than those forecast
    row_0 = temps.index[0] # We want to end when window date is equal to row_0.
    
    temps_list = [] # temporary holder of weeeks values.
    while window_date >= row_0:
        true_temp = int(temps.loc[actual_date][0]) # True temperature recorded on day
        predicted_temp = int(temps.loc[window_date][window]) # data predicted on value of window
        difference =  true_temp - predicted_temp
        # loop 
        actual_date -= pd.DateOffset(days=1) # take off 1 day.
        window_date -= pd.DateOffset(days=1) # take off 1 day.
        # append
        temps_list.append(difference)    
    # Add list to df as series    
    fac[columns[j]] = pd.Series(temps_list[::-1]) # Add list backwards.
        
fac.index = basic_dates

# Display Heatmap
st.write("""
#### Heatmap of Forecast Accuracy   
""")
heat_map(fac,"Forecast Variation (0 = 100% Accurate)")

st.write("""
# PART 4: Build Persistence Model
- Build models for  Weather(t+i) = Weather(t)
""")
# Persistance Mechanism subtract each max temp from the one before.
pmodel  = pd.Series([today - yesterday for today,yesterday in zip(temps['today+0'],temps['today+0'][1:])],index=temps.index[:len(temps.index)-1])

st.write("""
#### Persistence Series
# """)
st.dataframe(pmodel)


st.write("""
#### Persistence Accuracy 0 = Accurate +/- ºC above and below forecast
""")
st.line_chart(pmodel)
st.write(""" This shows that the persistance model we have is correct as each value in the list is the sum of the sequential temperature value subtracted. This gives us a baseline for how accurate "Tomorrow's weather will be the same as today" was for the days observed to date. """)

st.write(""" 
# PART 5: Compare the two models
- Compare Persistance to the forecasts provided by the BOM
""")

persistence = pd.DataFrame()
persistence['Persistence Accuracy'] = pmodel.values
for i in range(1,7):
    persistence[str(i)+' Day Forecast'] = pd.Series(fac['today+'+str(i)].values)
persistence.index = basic_dates[:len(basic_dates)-1]

# Display the DataFrame
st.dataframe(persistence)

# Display a Heatmap of the Persistence Accuracy
heat_map(persistence,"Persistence (far left) vs Forecast")

st.write(""" 
It appears that the persistance model may be a good benchmark for forecasts greater than 4 days away.   
To summarise, if you were to wager that the weather on a date 5 days from now, would be the closer to that of the day before rather than what the BOM has forecast, you would likely win.   

This suggests the feasibility of using the persistence model as a weighted feature in forecasts.
""")

st.write(""" 
# PART 6: Can we use the Persistence model as a feature?
This section wil attemtp to use historical data from the BOM with common forecasting models Facebook Prophet and Random Forest to see if combined with a Persisence model, we can forecast more accurately than the BOM.
""")

st.write(""" 
## Please watch this space for future development.
# """)