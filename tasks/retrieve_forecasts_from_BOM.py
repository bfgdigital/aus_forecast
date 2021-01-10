# Schedule.py Pulls forecast data from the BOM each day and saves it in an SQL db.

import pandas as pd  # Structure and Dataframes
import datetime as dt  # Time Functions
from datetime import datetime, timedelta
import requests  # API fetching

# SQL & Credentials Mgnt
import sqlalchemy
import os
import dotenv  # Protect db creds

dotenv.load_dotenv()

def fetch_db():
    print('LOG: Fetching database')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    engine = sqlalchemy.create_engine(DATABASE_URL)
    db = pd.read_sql('bom-weather', engine)
    return db, engine

def retrieve_forecasts():
    
    db, engine = fetch_db()
    # Define Reference Times
    today = dt.date.today()
    print(f'LOG: Connecting to database at {today}')

    # Build index checklist
    dates_index = list(set(db['issue']))  # create string based index
    dates_index.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%d'))  # Sort string indexes as dates

    # Forecast Locations
    # More URL's can be found via https://weather.bom.gov.au/search & talking the location reference from the URL
    # Eg: https://weather.bom.gov.au/location/r1r5rjm-clonbinane << 'r1r5rjm'
    locations = {
        'Melbourne': 'https://api.weather.bom.gov.au/v1/locations/r1r0fsn/forecasts/daily',
    }

    if str(today) in set(dates_index):
        print(f'LOG: Database already updated today {today}')
    else:
        # Fetch Location from location dicts.
        for name, url in locations.items():
            print(f'LOG: Fetching: {name}')
            response = requests.get(url).json()  # API Forecast as json
            af = pd.DataFrame(response['data'])  # Dict has 'data' and 'meta'
            # Process json data
            # Set forecast Dates
            af['issue'] = today
            af['forecast'] = [i for i in range(len(af))]
            # Set Location
            af['location'] = name
            # Split rain
            af['rain_min'] = [row['amount']['min'] for row in af['rain']]
            af['rain_max'] = [row['amount']['max'] for row in af['rain']]
            af['rain_max'].fillna(0, inplace=True)  # Rain Max is na if no rain forecast.
            af['rain_prob'] = [row['chance'] for row in af['rain']]
            # Split UV
            af['uv_cat'] = [row['category'] for row in af['uv']]
            af['uv_index'] = [row['max_index'] for row in af['uv']]
            # Split astronomical (Note: times are UTC)
            af['sunrise'] = [row['sunrise_time'] for row in af['astronomical']]
            af['sunset'] = [row['sunset_time'] for row in af['astronomical']]
            # Clean Up
            af.drop(['rain', 'uv', 'astronomical', 'now'], axis=1, inplace=True)
            af = af.reindex(sorted(af.columns), axis=1)
            # Add new data to forecast and push back into DB
            db = db.append(af)
            db.drop_duplicates(subset=db.columns.difference(['date']), keep='last', inplace=True,
                               ignore_index=True)  # In the case of pulling x2 in one day.
            db.to_sql('bom-weather', engine, if_exists='replace', index=False)
            print(f'LOG: Added new rows for {location} to db without problems.', '\n')
    print('LOG: Forecasts retrieved and stored without errors.', '\n')
    
def error_check(): # Impute any missing data.
    
    db, engine = fetch_db()
    db_check = len(db)
    
    def build_dates_index(db): # Build index checklist
        dates_index = list(set(db['issue']))  # create string based index
        dates_index.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%d'))  # Sort string indexes as dates
        return dates_index
    
    print('LOG: Checking for missing data')
    
    dates_index = build_dates_index(db)  # Get a list of issue dates.
    
    missing_dates = pd.date_range(start = dates_index[0],
                      end = dates_index[-1]).difference(pd.to_datetime(dates_index))    
    
    print('LOG: Checking for missing dates')
    for date in missing_dates:
        print(f'LOG: Adding missing date: {date}')
        str_date = date.strftime('%Y-%m-%d')
        day_before = (date - timedelta(days=1)).date()  # One Day prior
        day_after = (date + timedelta(days=1)).date()  # Day after

        # Take last 6 from day before [1:7] as (0:5)
        # and second last from day after [6:7] as (6)
        forecasts_0 = (db[db['issue'] == str(day_before)][1:7])  # just 1
        forecasts_1to7 = db[db['issue'] == str(day_after)][5:6]  # not inc. 7
        new_rows = pd.concat([forecasts_0,forecasts_1to7], axis=0)
        new_rows['forecast'] = [0,1,2,3,4,5,6]
        new_rows['issue'] = str_date
        db = db.append(new_rows)
    
    dates_index = build_dates_index(db) # Rebuild a list of issue dates.
    
    print('LOG: Checking for missing forecasts')
    for date in dates_index:
        day_after = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).date()  # Day after
        if len(db[db['issue'] == date]) == 6:
            try:
                print(f'LOG: Adding missing forecast for: {date}')
                new_forecast = db[db['issue'] == str(day_after)][5:6]  # not inc. 7
                new_forecast['forecast'] = 6
                new_forecast['issue'] = date
                db = db.append(new_forecast)
            except:
                print(f'LOG: No future date available for: {date}')

    db.drop_duplicates(subset=db.columns.difference(['date']), keep='last', inplace=True,
               ignore_index=True)  # In the case of pulling x2 in one day.
    
    # If no changes are made, do not write to file.
    if len(db) != db_check:
        print('LOG: Writing corrected db...', '\n')
        db.to_sql('bom-weather', engine, if_exists='replace', index=False)
        print('LOG: DB errors resolved.', '\n')
    else:
        print('LOG: No DB errors to resolve', '\n')