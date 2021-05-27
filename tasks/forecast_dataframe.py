import pandas as pd
import numpy as np
import datetime as dt  # Time Functions
from datetime import datetime
import sqlalchemy  # SQL and Credentials
import os
import io
import dotenv  # Protect db creds

dotenv.load_dotenv()

# SQL Connection
DATABASE_URL = os.environ.get('DATABASE_URL')

# stores the db in memory, slightly more efficient.
def get_database_connection():
    
    print('LOG: Fetching database...')
    
    engine = sqlalchemy.create_engine(DATABASE_URL)
    query = 'SELECT issue, MAX(CASE WHEN forecast = 0 THEN temp_max END) AS "today+0", MAX(CASE WHEN forecast = 1 THEN temp_max END) AS "today+1", MAX(CASE WHEN forecast = 2 THEN temp_max END) AS "today+2", MAX(CASE WHEN forecast = 3 THEN temp_max END) AS "today+3", MAX(CASE WHEN forecast = 4 THEN temp_max END) AS "today+4", MAX(CASE WHEN forecast = 5 THEN temp_max END) AS "today+5", MAX(CASE WHEN forecast = 6 THEN temp_max END) AS "today+6" FROM "bom-weather" GROUP BY issue ORDER BY issue'

    # Store db in memory for speed up?
    copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
        query=query, head="HEADER"
    )
    conn = engine.raw_connection()
    cur = conn.cursor()
    store = io.StringIO()
    cur.copy_expert(copy_sql, store)
    store.seek(0)
    mem_stored_db = pd.read_csv(store)
    
    #  Fetch the extended text description of the last row.
    query2 = 'SELECT extended_text FROM "bom-weather" ORDER BY issue DESC LIMIT 1'
    last_row = pd.read_sql_query(query2, engine)
    
    # Incase whole db is req.
    #     mem_stored_db = pd.read_sql('bom-weather', engine)  
    #     mem_stored_db = mem_stored_db.sort_values(['issue', 'forecast', 'date'], ascending=[True, True, True]) # sort the dataframe
    
    return mem_stored_db, last_row


def build_dates_index(db):  # Build index checklist
    dates_index = list(set(db['issue']))  # create string based index
    dates_index.sort(key=lambda date: datetime.strptime(
        date, '%Y-%m-%d'))  # Sort string indexes as dates
    return dates_index


def build_forecast_dataframe():
    

    # Justify function to shift NaN's to correct side of db.
    def justify(a, invalid_val=0, axis=1, side='left'):
        if invalid_val is np.nan:
            mask = ~np.isnan(a)  # Reversing logical value ~x is equivalent to (-x) - 1
        else:
            mask = a!=invalid_val
        justified_mask = np.sort(mask,axis=axis)
        if (side=='up') | (side=='left'):
            justified_mask = np.flip(justified_mask,axis=axis)
        out = np.full(a.shape, invalid_val) 
        if axis==1:
            out[justified_mask] = a[mask]
        else:
            out.T[justified_mask.T] = a.T[mask.T]
        return out
    
    # Create accuracy table by compare forecast T>0 to T0
    db, last_row = get_database_connection()

    dates_index = build_dates_index(db)  # set the index to the dataframe.
    
    db.index = pd.to_datetime(db.index)  # Change the new index back into datetime.
    db.drop('issue',axis=1,inplace=True)

    holder = []
    for i in range(7):
        tf0 = db['today+0']
        holder.append(tf0 - db['today+'+(str(i))].shift(i))  # Using the shift function
    forecast_accuracy = pd.DataFrame(holder).T
    forecast_accuracy[:] = justify(forecast_accuracy.values, invalid_val=np.nan, axis=0, side='up')
    forecast_accuracy.columns = db.columns  # replace col names.

    # Replace original index with non-datetime indexes.
    forecast_accuracy.index = dates_index  # same index
    db.index = dates_index  # same index
    
    #################################
    # Persistence
    ################################

    # Persistence Mechanism subtract each max temp from the one before.
    pmodel = pd.Series([today - yesterday for today, yesterday in zip(db['today+0'], db['today+0'][1:])], index=db.index[:len(db.index)-1])

    # Assign pmodel vals to series.
    persistence = pd.DataFrame()
    persistence['Persistence Accuracy'] = pmodel.values
    for i in range(1, 7):
        persistence[str(i)+' Day Forecast'] = pd.Series(forecast_accuracy['today+'+str(i)].values)
    persistence.index = dates_index[:len(db)-1]


    #################################
    # Save to file
    ################################

    db.to_csv('./static/data/forecast_dataframe.csv')
    forecast_accuracy.to_csv('./static/data/accuracy_dataframe.csv')
    persistence.to_csv('./static/data/persistence_dataframe.csv')
    last_row.to_csv('./static/data/last_row.csv')

    print('Forecast & Accuracy CSV Saved without errors.', '\n')
