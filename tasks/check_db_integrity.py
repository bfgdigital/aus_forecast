# Checking the intergrity of the forecast API data and imputing as necessary.

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
    print('LOG: Fetching database...')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    engine = sqlalchemy.create_engine(DATABASE_URL)
    db = pd.read_sql('bom-weather', engine) # Need the whole db.
    return db, engine

def integrity_check(): # Impute any missing data.
    
    db, engine = fetch_db()
    db_check = len(db)
    
    def build_dates_index(db): # Build index checklist
        dates_index = list(set(db['issue']))  # create string based index
        dates_index.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%d'))  # Sort string indexes as dates
        return dates_index
    
    print('LOG: Checking for missing data')
    
    dates_index = build_dates_index(db)  # Get a list of issue dates.
    
    missing_dates = pd.date_range(start = dates_index[0],
                      end = dates_index[-1]).difference(pd.to_datetime(dates_index))  # [::-1] (Reverse?)   
    
    print('LOG: Checking for missing dates')
    for date in missing_dates:
        print(f'LOG: Adding missing date: {date}')
        str_date = date.strftime('%Y-%m-%d')
        day_before = (date - timedelta(days=1)).date()  # One Day prior
        day_after = (date + timedelta(days=1)).date()  # Day after

        # THIS NEEDS WORK. BIT SLOPPY
        # Take last 6 from day before [1:7] as (0:5)
        # and second last from day after [6:7] as (6)
        try:
            
            part2 = db[db['issue'] == str(day_before)][6:7]  # day 7
            part1 = db[db['issue'] == str(day_after)][1:7]  # day 1:6
            print(f'len of part1 = {len(part1)}')
            print(f'len of part2 = {len(part2)}')
            new_rows = pd.concat([part1, part2], axis=0)
            new_rows['forecast'] = [0,1,2,3,4,5,6]
            new_rows['issue'] = str_date
            db = db.append(new_rows)
        except:
            pass

        try:
            part2 = db[db['issue'] == str(day_before)][0:6]  # day 1:6
            part1 = db[db['issue'] == str(day_after)][1:2]  # day 7
            print(f'len of part1 = {len(part1)}')
            print(f'len of part2 = {len(part2)}')
            new_rows = pd.concat([part1, part2], axis=0)
            new_rows['forecast'] = [0,1,2,3,4,5,6]
            new_rows['issue'] = str_date
            db = db.append(new_rows)
        except:
            # When there are dates either side of date in missing_dates
            # this solution cannot work.
            # Needs a wider excalation loop that can cover
            # multiple days before and behind.
            # OR we can run it multiple times (start to finish)
            print('\n!!! Missing dates integrity check failed!!!')
            print(f'{str_date}\n')
            continue
    
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
    db = db.reindex(sorted(db.columns), axis=1)  # Sort Cols alphabetically.
    
    # If no changes are made, do not write to file.
    if len(db) != db_check and len(db) > 600:
        print('LOG: Writing corrected db...', '\n')
        db.to_sql('bom-weather', engine, if_exists='replace', index=False)
        print('LOG: DB errors resolved.', '\n')
    else:
        print('LOG: No DB errors to resolve', '\n')
