# Persistance Model of BOM Weather

## Introduction

We often get a 7 day weather forecast but don't often go back to see how accurate the predictions were for 7 days ago.
This project looks to explore how accurate the weather forecast is according to a what is known as the Persistance Model.
The Persistance Model hypothesis for the weather domain is that "The weather tomorrow will be the same as today",   
or in mathematical terms Weather(t+1) = Weather(t), (t being today, or time).

The forecasts are already known to be very accurate for t = 1,2 and 3, so for this project I will be looking at t+7.

The persistence model, also called the naïve predictor, is often used as a reference as it is a good ground estimation of other algorithms,   
and often used as a reference for determining the skill factor of a competing forecast model.

<img src="assets/forecast.png" width="32%" /><img src="assets/accuracy.png" width="32%" /><img src="assets/persistence.png" width="32%" />

After the persistence model is evaluated, historical weather data is used to try and improve upon the persistance model using Facebook Prophet and Random Forest Regressor.
The new forecast is saved to ben_vs_bom.csv and will be built upon over time.

* [Part 1 is now live](http://bom-weather.herokuapp.com) - bom_app.py & scheduler.py on Heroku via Streamlit & Postgres.

**Updated to a 2 day forecast.**

<img src="assets/my_forecasts.png" width="70%" />

## Important Links

* [Final Report Notebook](report.ipynb)
* [EDA Notebook](eda.ipynb)
* [BOM Data](ftp://ftp.bom.gov.au/anon/gen/fwo/) - XML files for all weather reports in Australia. (ftp link)
* [Melbourne Forecast File](ftp://ftp.bom.gov.au/anon/gen/fwo/IDV10450.xml) - The Melbourne forecast file. (ftp link)
* [BOM API](https://api.weather.bom.gov.au/v1/locations/r1r143/forecasts/daily) - API data. Be aware the feed is updated every 10mins.
* [fbprophet](https://facebook.github.io/prophet/docs/quick_start.html) - Facebook Prophet timeseries forecasting package.
* [Random Forest Regressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html) - Scikit Learn's Random Forest Regressor.
