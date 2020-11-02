#################################
# Imports
################################

import streamlit as st # Web App
import pandas as pd # Dataframes
import numpy as np # Maths functions
import datetime as dt # Time Functions
import requests # API fetching
from sklearn.metrics import mean_squared_error # Mean Squared Error Function (Needs np.sqrt for units)

# Charting
from matplotlib import pyplot as plt
import seaborn as sns

# SQL and Credentials
import os
import dotenv # Protect db creds
dotenv.load_dotenv()
import sqlalchemy

# SQL Connection
DATABASE_URL = os.environ.get('DATABASE_URL')
# Cache func for loading Database.
@st.cache(allow_output_mutation=True)
def get_database_connection():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    db = pd.read_sql('bom-weather', engine)
    return db

# Define Times (easier to just make a string format time here.)
today = dt.date.today()
todaystr = today.strftime("%Y-%m-%d")
yesterday = dt.date.today() - pd.DateOffset(days=1)
yesterdaystr = yesterday.strftime("%Y-%m-%d")
tomorrow = dt.date.today() + pd.DateOffset(days=1)
tomorrowstr = tomorrow.strftime("%Y-%m-%d")
day_after_tomorrow = dt.date.today() + pd.DateOffset(days=2)
day_after_tomorrowstr = day_after_tomorrow.strftime("%Y-%m-%d")

# Load Data
data_load_state = st.text('Loading data...') # Loading message
db = get_database_connection() # pull DB data.
data_load_state.text('Loading data...done!') # Data loaded message
db.index = pd.to_datetime(db['date']) # Set DB Index

#################################
# DataFrame
################################

#Build DataFrame from db
today0 = db[db['forecast'] == 0]
today1 = db[db['forecast'] == 1]
today2 = db[db['forecast'] == 2]
today3 = db[db['forecast'] == 3]
today4 = db[db['forecast'] == 4]
today5 = db[db['forecast'] == 5]
today6 = db[db['forecast'] == 6]

# Set Index
dates_index = list(set(db['issue']))
dates_index.sort() # Sort Index

# Dataframe for TF
tf = pd.DataFrame(None)
tf['today+0'] = today0['temp_max'].reset_index(drop=True)
tf['today+1'] = today1['temp_max'].reset_index(drop=True)
tf['today+2'] = today2['temp_max'].reset_index(drop=True)
tf['today+3'] = today3['temp_max'].reset_index(drop=True)
tf['today+4'] = today4['temp_max'].reset_index(drop=True)
tf['today+5'] = today5['temp_max'].reset_index(drop=True)
tf['today+6'] = today6['temp_max'].reset_index(drop=True)

tf.index = dates_index

#################################
# Heatmap
################################

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
    return st.pyplot(fig);


#################################
# Accuracy
################################

# Create Accuracy Table
tf.index = pd.to_datetime(tf.index) # make index a datetime.

# Acuracy Mechanism: Compare forecast to actual Temp.
fac = pd.DataFrame()
counter = list(range(len(tf)))
columns = list(tf.columns)

for i in counter:
    # 7 day forecast inc today, so len can't exceed 7
    if i < 7:
        window = i 
        j = i
    else: 
        window = 6
        j = 6
    
    # Start date at most recent row
    actual_date = tf.index[-1] # start with the last day
    window_date = actual_date - pd.DateOffset(days=window) # Number of days in the past can't be more than those forecast
    row_0 = tf.index[0] # We want to end when window date is equal to row_0.
    
    tf_list = [] # temporary holder of weeeks values.
    while window_date >= row_0:
        true_temp = int(tf.loc[actual_date][0]) # True temperature recorded on day
        predicted_temp = int(tf.loc[window_date][window]) # data predicted on value of window
        difference =  true_temp - predicted_temp
        # loop 
        actual_date -= pd.DateOffset(days=1) # take off 1 day.
        window_date -= pd.DateOffset(days=1) # take off 1 day.
        # append
        tf_list.append(difference)    
    # Add list to df as series    
    fac[columns[j]] = pd.Series(tf_list[::-1]) # Add list backwards.
        
fac.index = dates_index
tf.index = dates_index

#################################
# RMSE
################################
data_load_state.text('Loading data...done!')
# Assign (Root) Mean Squared Error
rmse_today1 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+1'].dropna())],fac['today+1'].dropna()))]
rmse_today2 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+2'].dropna())],fac['today+2'].dropna()))]
rmse_today3 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+3'].dropna())],fac['today+3'].dropna()))]
rmse_today4 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+4'].dropna())],fac['today+4'].dropna()))]
rmse_today5 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+5'].dropna())],fac['today+5'].dropna()))]
rmse_today6 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+6'].dropna())],fac['today+6'].dropna()))]

# Assign error vals to a df
accuracy = pd.DataFrame()
accuracy['1 Day Forecast'] = rmse_today1
accuracy['2 Day Forecast'] = rmse_today2
accuracy['3 Day Forecast'] = rmse_today3
accuracy['4 Day Forecast'] = rmse_today4
accuracy['5 Day Forecast'] = rmse_today5
accuracy['6 Day Forecast'] = rmse_today6

#################################
# Persistence
################################

# Persistance Mechanism subtract each max temp from the one before.
pmodel  = pd.Series([today - yesterday for today,yesterday in zip(tf['today+0'],tf['today+0'][1:])],index=tf.index[:len(tf.index)-1])

# Assign pmodel vals to series.
persistence = pd.DataFrame()
persistence['Persistence Accuracy'] = pmodel.values
for i in range(1,7):
    persistence[str(i)+' Day Forecast'] = pd.Series(fac['today+'+str(i)].values)
persistence.index = dates_index[:len(dates_index)-1]

#Assign RMSE value for pmodel
persistence_rmse = np.sqrt(mean_squared_error(pmodel,fac['today+0'][:len(fac)-1]))


#################################
#################################
# Display
################################
#################################

# App Begins
st.write("""
# Melbourne Forecast Accuracy

### Evaluating the accuracy of the Bureau of Meteorology 6 day forecast.
The following information is an examination of the Bureau of Meteorology's 6-day forecast. It uses two methods of evaluation.

1) It looks at the error (Root Mean Squared Error or RMSE) of how correct/incorrect forecasts are by day (eg: how accurate is the 3-day forecast).    
2) Secondly it looks at how accurate the forecast is against a nieve forecasting approach. In this case the persistence model. Which states "The weather tomorrow will be the same as today" ie: the temperature will persist. This is a good way to evaluate model accuracy during times of variation, which is the primary goal of accurate forecasting. Allowing people to adapt to changes in the weather.
""")

st.write("""
#### Summary of Data
""")
# Summary
st.text(f"Today\'s date is: {today}")
st.text(f"New forecasts:	{len(db)}, Starting on: {db['issue'][0]}, Ending on: {db['issue'][len(db)-1][:10]}")
todays_forecast = f"#### Today's forecast: \n >*{db['extended_text'][0]}*"
st.markdown(todays_forecast)

# Display Previous Data Heatmap Description
st.write("""
#### 1.1: Heatmap of previous Max-Temp forecasts.
Reading this chart, each value shifts one space to the left for each descending row as the 6-day forecast becomes day 5, 4, 3 .. etc. Today + 0 is the temperature forecast for that particular day. As this only looks forwards, Today + 0 is still a forecast. Working with historical data will be added in future versions, but it is for the most part, extremely accurate and serves the purposes of this project.
# """)

# Previous Data Heatmap
heat_map(tf,"7 Day Forecasts From BOM (Decending to the left)")

# Variation Heatmap Description
st.write("""
#### 1.2: Heatmap of Forecast Accuracy   
This chart shows how accurate the forecasts were against the actual temperature. There is no need to read down and to the left, the cells show how accurate the forecast was, once the date of the forecast has passed. As the days in the bottom right corner have not occurred yet, (this coming week) there is no way to evaluate the accuracy.
""")

# Variation Heatmap
heat_map(fac,"Forecast Variation (0 = 100% Accurate)")

# RMSE Values
st.write("""
#### 1.3: RMSE Accuracy of predictions
This table shows how many degrees the forecasts is likely to fall between.
so for a value of 2, the forecasts is likely to be within 2ºC higher or lower of that which they forecast.
# """)
st.dataframe(accuracy)


# Chart accuracy
st.write("""
#### 1.4: Line Chart of Accurcay
As the date forecast gets further away, the average error increases.
""")
st.line_chart(accuracy.T)

# PART 2
st.write("""
## PART 2: Persistence
Evaluating against Weather(t+i) = Weather(t).
This compares the accuracy of the forecast against the nieve model of "Tomorrow's max-temp will be the same as today". This comparison shows how much the weather changes according to the day before it. As cool and warm fronts come through, the temperature changes significantly. This is where the persistence model is a weak predictor.
""")

st.write("""
#### 2.1: Persistence Accuracy +/- ºC above and below forecast
""")
col1, col2 = st.beta_columns([2, 2])

col1.subheader("Difference in ºC \n from the previous day")
col1.dataframe(pmodel)

peristance_info = f"#### Persistence RMSE: \n **{persistence_rmse}** \n >This is the current mean error of the persistence model."
col2.subheader("Persistence Mean Error")
col2.markdown(peristance_info)

st.write("""
#### 2.2: Persistance Variation by Day 
Displayed as a bar chart
""")
# Persistence DataFrame
st.bar_chart(pmodel)

# Variation Heatmap Description
st.write("""
#### 2.3: Heatmap of Persistence Accuracy   
Here you can compare how accurate the persistence model was vs the BOM forecast for any given day.
As the days get further away, the accuracy of the persistence and BOM forecast becomes more even.
""")
# Display a Heatmap of the Persistence Accuracy
heat_map(persistence,"Persistence (far left) vs Forecast")

st.write(""" 
It appears that the persistence model may be a good benchmark for forecasts greater than 4 days away.   

To summarise, if you were to wager that the weather on a date 5 days from now, would be the closer to that of the day before, rather than what the BOM has forecast, you would likely win.   

This suggests the feasibility of exploring the persistence model as a weighted feature for future forecasts.
""")
        
st.write("""
#### DATA Sources 
- Data Comes From: ftp://ftp.bom.gov.au/anon/gen/fwo/
- Melbourne Forecast File: ftp://ftp.bom.gov.au/anon/gen/fwo/IDV10450.xml

The url for the BOM API is:
https://api.weather.bom.gov.au/v1/locations/r1r143/forecasts/daily   
Be Aware that the update is adjusted every 10mins.
""")

st.write(""" 
#### Please watch this space for future development.
# """)
        
        