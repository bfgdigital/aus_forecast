# Schedule.py Pulls required data and files and saves them to static or PostgreSQL.

import os
import sys

from tasks.task1_retrieve_forecasts_from_BOM import retrieve_forecasts
from tasks.task2_check_db_integrity import integrity_check
from tasks.task3_forecast_dataframe import build_forecast_dataframe
from tasks.task4_generate_heatmaps import generate_heatmaps
from training_data.task1_training_weather import build_training_dataframe
from tasks.task5_prophet_forecaster import build_prophet_forecaster

# Runs the following tasks daily.
def main():
    print('LOG: Starting - Retrieve Forecasts from API')
    retrieve_forecasts()  # Update the database.
    print('LOG: Complete - Retrieve Forecasts from API', '\n')
    
    print('LOG: Starting - Check database integrity')
    integrity_check()  # Check database for errors.
    print('LOG: Complete - Check database integrity', '\n')

    print('LOG: Starting - Build Forecast Dataframe')
    build_forecast_dataframe()  # Build and save a dataframe of the forecasts
    print('LOG: Complete - Build Forecast Dataframe', '\n')
    
    print('LOG: Starting - Predict Prophet Forecasts')
    generate_heatmaps()  # Train, fit and save prophet forecasts.
    print('LOG: Complete - Predict Prophet Forecasts', '\n')

#     print('LOG: Starting - Build Training Dataframe')
#     build_training_dataframe()  # Build and save the training data.
#     print('LOG: Complete - Build Training Dataframe')

#     print('LOG: Starting - Predict Prophet Forecasts')
#     build_prophet_forecaster()  # Train, fit and save prophet forecasts.
#     print('LOG: Complete - Predict Prophet Forecasts', '\n')
    
    print('LOG: Scheduler Complete')

main()
