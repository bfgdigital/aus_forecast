# Schedule.py Pulls forecast data from the BOM each day and saves it in an SQL db.

import pandas as pd  # Structure and Dataframes
import datetime as dt  # Time Functions
from datetime import datetime
import requests  # API fetching

# SQL & Credentials Mgnt
import sqlalchemy
import os
import dotenv  # Protect db creds

dotenv.load_dotenv()


def retrieve_forecasts():
    # Define Reference Times
    today = dt.date.today()

    # SQL Connection
    DATABASE_URL = os.environ.get('DATABASE_URL')
    engine = sqlalchemy.create_engine(DATABASE_URL)
    print(f'LOG: Connecting to database at {today}')
    db = pd.read_sql('bom-weather', engine)

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
            # db.to_sql('bom-weather', engine, if_exists='replace', index=False)
            print(f'LOG: Added new rows to db without problems.')

    print('LOG: Forecasts retrieved and stored without errors.', '\n')
