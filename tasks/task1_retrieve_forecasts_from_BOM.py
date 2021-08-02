# Schedule.py Pulls forecast data from the BOM each day and saves it in an SQL db.

import pandas as pd  # Structure and Dataframes
import datetime as dt  # Time Functions
from datetime import datetime
import requests  # API fetching

# SQL & Credentials Management
import sqlalchemy
import os
import dotenv  # Protect db credentials

dotenv.load_dotenv()


def fetch_db() -> pd.DataFrame:
    print('LOG: Fetching database')
    database_url = os.environ.get('DATABASE_URL')
    engine = sqlalchemy.create_engine(database_url)
    # Require whole db.
    # db = pd.read_sql('SELECT * FROM bom-weather ORDER BY "issue" DESC', engine)
    db = pd.read_sql_table("bom-weather", engine)
    return db, engine


def build_dates_index(db):  # Build index checklist
    dates_index = list(set(db['issue']))  # create string based index
    dates_index.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%d'))  # Sort string indexes as dates
    return dates_index


def rain(df: pd.DataFrame) -> pd.DataFrame:
    df_rain = df['rain'].apply(pd.Series)
    df_amount = df_rain['amount'].apply(pd.Series)
    df_amount['max'].fillna(float(0), inplace=True)
    rain = pd.concat([df_amount, df_rain['chance']], axis=1)
    return rain.add_prefix('rain_')


def uv(df: pd.DataFrame) -> pd.DataFrame:
    uv = df['uv'].apply(pd.Series)
    return uv.add_prefix('uv_')


def astronomical(df: pd.DataFrame) -> pd.DataFrame:
    astronomical = df['astronomical'].apply(pd.Series)
    return astronomical.add_prefix('astronomical_')


def metadata(df: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    issue = pd.Series([TODAY for _ in range(len(df))], name='issue')
    forecast = pd.Series([i for i in range(len(df))], name='forecast')
    location = pd.Series([name for _ in range(len(df))], name='location')
    date = df['date']
    now = df['now'].apply(pd.Series).drop(0, inplace=True, axis=1)  # drop the 0's
    forecast_metadata = df2
    metadata = pd.concat([issue, forecast, location, now, forecast_metadata], axis=1)
    return metadata


def forecast(df, df2) -> pd.DataFrame:
    non_nested = df[['temp_max', 'temp_min', 'extended_text',
                     'icon_descriptor', 'short_text', 'fire_danger']]
    forecast_data = pd.concat([non_nested, rain(df), uv(df), astronomical(df), metadata(df, df2)], axis=1)
    return forecast_data


def retrieve_forecasts():
    db, engine = fetch_db()
    # Define Reference Times
    today = dt.date.today()
    print(f'LOG: Connecting to database at {today}')

    dates_index = build_dates_index(db)

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
            # Flatten the JSON object.
            df = pd.DataFrame.from_dict(response['data'])
            df2 = pd.DataFrame(response['metadata'], index=[0])
            # Call it all together
            forecast_data = forecast(df, df2)
            # Add new data to forecast and push back into DB
            db = db.append(forecast_data)
            db.drop_duplicates(subset=db.columns.difference(['date']), keep='last', inplace=True,
                               ignore_index=True)  # In the case of pulling x2 in one day.
            # db.to_sql('bom-weather', engine, if_exists='replace', index=False)
            print(f'LOG: Added new rows for {location} to db without problems.', '\n')
    print('LOG: Forecasts retrieved and stored without errors.', '\n')
