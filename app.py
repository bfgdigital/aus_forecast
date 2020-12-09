#################################
# Imports
################################

import streamlit as st  # Web App
import pandas as pd  # Dataframes
import numpy as np  # Maths functions
import datetime as dt  # Time Functions
from datetime import datetime

# SKLearn
from sklearn.metrics import mean_squared_error  # Mean Squared Error Function (Needs np.sqrt for units)

# load data
tf = pd.read_csv('./static/data/forecast_dataframe.csv', index_col=0)  # Whole csv. Much faster than accessing db.
fac = pd.read_csv('./static/data/accuracy_dataframe.csv', index_col=0)  # Whole csv. Much faster than accessing db.
persistence = pd.read_csv('./static/data/persistence_dataframe.csv', index_col=0)
last_row = pd.read_csv('./static/data/last_row.csv', index_col=0)

today = dt.date.today()
todaystr = today.strftime("%Y-%m-%d")


#################################
# RMSE
################################

# Assign (Root) Mean Squared Error
rmse_today1 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+1'].dropna())], fac['today+1'].dropna()))]
rmse_today2 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+2'].dropna())], fac['today+2'].dropna()))]
rmse_today3 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+3'].dropna())], fac['today+3'].dropna()))]
rmse_today4 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+4'].dropna())], fac['today+4'].dropna()))]
rmse_today5 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+5'].dropna())], fac['today+5'].dropna()))]
rmse_today6 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+6'].dropna())], fac['today+6'].dropna()))]

# Assign error vals to a df
accuracy = pd.DataFrame()
accuracy['1 Day Forecast'] = rmse_today1
accuracy['2 Day Forecast'] = rmse_today2
accuracy['3 Day Forecast'] = rmse_today3
accuracy['4 Day Forecast'] = rmse_today4
accuracy['5 Day Forecast'] = rmse_today5
accuracy['6 Day Forecast'] = rmse_today6

accuracy.index = ["Average Daily Forecast Error"]

#################################
# VS RMSE
################################

# Assign RMSE value for pmodel
persistence_rmse = np.sqrt(mean_squared_error(persistence['Persistence Accuracy'], fac['today+0'][:len(fac)-1]))

persistence_vs = pd.DataFrame()
persistence_vs['1 Day Error'] = accuracy['1 Day Forecast'] - persistence_rmse
persistence_vs['2 Day Error'] = accuracy['2 Day Forecast'] - persistence_rmse
persistence_vs['3 Day Error'] = accuracy['3 Day Forecast'] - persistence_rmse
persistence_vs['4 Day Error'] = accuracy['4 Day Forecast'] - persistence_rmse
persistence_vs['5 Day Error'] = accuracy['5 Day Forecast'] - persistence_rmse
persistence_vs['6 Day Error'] = accuracy['6 Day Forecast'] - persistence_rmse

persistence_vs.index = ["BOM Error vs Persistence Error"]

#################################
#################################
# Display
################################
#################################

# App Begins
st.write("""
# Melbourne Forecast Accuracy

### Evaluating the accuracy of the Bureau of Meteorology 6 day forecast.
The following information is an examination of the Bureau of Meteorology's 6-day forecast.

It's hard to know if a forecast is good because it depends on how *'good'* is measured.
Is accurate to within 1º good? How about within 5º?   

This project is evaluating how accurate forecasts are, ***depending on how many days away the forecast is.***
So instead of comparing to the historical temperatures, this will just look at how much the forecast changes as the date gets closer.   

Firstly, it looks at the error (Root Mean Squared Error or RMSE) of how correct/incorrect forecasts are by day (eg: how similar is the 3-day forecast compared to the same day forecast).    
Secondly, it evaluates at how accurate the forecast is against a naive forecasting approach, in this case the persistence model which is simply *"The weather tomorrow will be the same as today"* ie: the temperature will persist. 
This is a good way to evaluate model accuracy as this form of forecast naturally varies with changing weather, which makes it comparable to the difficulties typically faced in weather forecasting.
""")

st.write("""
#### Summary of Data
""")
# Summary
st.text(f"Today\'s date is: {today}")
st.text(f"New forecasts:	{len(tf)}, Starting on: {tf.index[0]}, Ending on: {tf.index[-1]}")
todays_forecast = f"#### Today's forecast: \n >*{last_row['extended_text'][0]}*"
st.markdown(todays_forecast)

# Display Previous Data Heatmap Description
st.write("""
#### 1.1: Heatmap of previous Max-Temp forecasts.
Reading this chart, each value shifts one space to the left for each descending row as the 6-day forecast becomes day 5, 4, 3 .. etc. Today + 6 on the first row becomes Today+5 on the second row, Today+4 on the third row. 
As this project only uses forecast data, (no past recorded temperatures), Today + 0 is still a forecast. Working with historical data will be added in future versions, but it is for the most part, Today+0 is very accurate and serves the purposes of this project.
# """)

# Previous Data Heatmap
st.image('./static/charts/heatmap_forecast.png', use_column_width=True)

# Variation Heatmap Description
st.write("""
#### 1.2: Heatmap of Forecast Accuracy   
This chart shows how accurate the forecasts were against the actual temperature. There is no need to read down and to the left, the cells show how accurate the forecast was, once the date of the forecast has reached Today+0. As the days in the bottom right corner have not occurred yet, (this coming week) there is no way to evaluate the accuracy.
""")

# Variation Heatmap
st.image('./static/charts/heatmap_accuracy.png', use_column_width=True)

# RMSE Values
st.write("""
#### 1.3: RMSE Accuracy of predictions
This table shows how many degrees the forecasts is likely to fall between.
so for a value of 2, the forecasts is likely to be within 2ºC higher or lower of that which they forecast.
# """)
st.dataframe(accuracy)


# Chart accuracy
st.write("""
#### 1.4: Line Chart of Forecast Accuracy
As the forecast moves further into the future, the average forecast error increases.
""")
st.line_chart(accuracy.T)

# PART 2
st.write("""
## PART 2: Persistence
Evaluating against Weather(t+i) = Weather(t).
This compares the accuracy of the forecast against the naive model of "Tomorrow's max-temp will be the same as today". This comparison shows how much the weather changes according to the day before it. As cool and warm fronts come through, the temperature changes significantly. This is where the persistence model is a weak predictor.
""")

st.write("""
#### 2.1: Persistence Mean Error +/- ºC above and below forecast
""")

persistence_info = f"#### Persistence RMSE: \n **{persistence_rmse}** \n >This is the current mean error of the persistence model."
st.markdown(persistence_info)

st.write("""
#### 2.2: Persistence Variation by Day 
Each bar is the difference in temperature from the day before.
""")
# Persistence DataFrame
st.bar_chart(persistence['Persistence Accuracy'])

# Variation Heatmap Description
st.write("""
#### 2.3: Heatmap of Persistence Accuracy   
Here you can compare how accurate the persistence model was vs the BOM forecast for any given day.
As the days get further away, the accuracy of the persistence and BOM forecast becomes more even.
""")

# Display a Heatmap of the Persistence Accuracy
st.image('./static/charts/heatmap_persistence.png', use_column_width=True)

# Persistence vs
st.write("""
#### 2.4: RMSE Accuracy of Persistence predictions
The error for persistence should be constantly changing depending on the swing in the weather,
however 
# """)
st.dataframe(persistence_vs)

# Chart accuracy
st.write("""
#### 2.5: BOM VS Persistence
This chart shows (BOM RMSE - Persistence RMSE), in other words, how much more accurate is the BOM than Persistence.
As the forecast error increases with each day further into the future that is predicted, the difference in error between the models becomes smaller.
Here you can see see that for 1 day into the future, the BOM is over +/-3º more accurate than a persistence model, but by the 6th day, it's less than 1º more accurate.
""")

# Display barchart
st.bar_chart(persistence_vs.T)

st.write(""" 
It appears that the persistence model may be a good benchmark for forecasts greater than 6 days away.
It also hints at why the BOM doesn't typically offer longer forecasts like a 10 or 14 day forecast.
To summarise, it looks like the Bureau is doing a good job of predicting something notoriously difficult to forecast. 
""")
        
st.write("""
#### DATA Sources 
- Data Comes From: ftp://ftp.bom.gov.au/anon/gen/fwo/
- Melbourne Forecast File: ftp://ftp.bom.gov.au/anon/gen/fwo/IDV10450.xml
""")

st.write(""" 
#### Please watch this space for future development.
# """)
