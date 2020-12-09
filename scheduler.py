# Schedule.py Pulls required data and files and saves them to static or PostgreSQL.

import os
import sys

from tasks.retrieve_forecasts_from_BOM import retrieve_forecasts
from tasks.forecast_dataframe import build_forecast_dataframe
from training_data.training_weather import build_training_dataframe
from tasks.generate_heatmaps import generate_heatmaps
from tasks.prophet_forecaster import build_prophet_forecaster


def main():
    print('LOG: Starting - Retrieve Forecasts from API')
    retrieve_forecasts()  # Update the database.
    print('LOG: Complete - Retrieve Forecasts from API')
    
    print('LOG: Starting - Build Forecast Dataframe')
    build_forecast_dataframe()  # Build and save a dataframe of the forecasts
    print('LOG: Complete - Build Forecast Dataframe')
    
    print('LOG: Starting - Predict Prophet Forecasts')
    generate_heatmaps()  # Train, fit and save prophet forecasts.
    print('LOG: Complete - Predict Prophet Forecasts', '\n')

    # print('LOG: Starting - Build Training Dataframe')
    # build_training_dataframe()  # Build and save the training data.
    # print('LOG: Complete - Build Training Dataframe')

    # print('LOG: Starting - Predict Prophet Forecasts')
    # build_prophet_forecaster()  # Train, fit and save prophet forecasts.
    # print('LOG: Complete - Predict Prophet Forecasts', '\n')
    
    print('LOG: Scheduler Complete')

main()
