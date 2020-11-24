# Schedule.py Pulls required data and files and saves them to static or PostgreSQL.

import os
import sys

from tasks.retrieve_forecasts_from_BOM import retrieve_forecasts
from tasks.forecast_dataframe import build_forecast_dataframe
from training_data.training_weather import build_training_dataframe
from tasks.prophet_forecaster import build_prophet_forecaster


def main():
    retrieve_forecasts()  # Update the database.
    build_forecast_dataframe()  # Build and save a dataframe of the forecasts
    build_training_dataframe()  # Build and save the training data.
    build_prophet_forecaster()  # Train, fit and save prophet forecasts.
    print('Scheduler Complete')

main()
