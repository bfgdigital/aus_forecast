import pandas as pd
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
    engine = sqlalchemy.create_engine(DATABASE_URL)
    query = 'SELECT date, forecast, temp_max, issue, extended_text FROM "bom-weather"'

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

    #     db = pd.read_sql_query('SELECT date, forecast, temp_max, issue, extended_text FROM "bom-weather";',engine)
    #     db = pd.read_sql('bom-weather', engine)  # Don't need whole db
    return mem_stored_db


def build_forecast_dataframe():

    print('Beginning to build the forecast database')

    # Load Data
    db = get_database_connection()  # pull DB data.
    db.index = pd.to_datetime(db['date'])  # Set DB Index
    dates_index = list(set(db['issue']))  # create string based index
    dates_index.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%d'))  # Sort string indexes as dates

    #################################
    # Latest Info
    ################################

    last_row = db.tail(1)
    last_row.to_csv('./static/data/last_row.csv')

    #################################
    # DataFrame
    ################################

    # Build DataFrame from db
    today0 = db[db['forecast'] == 0]
    today1 = db[db['forecast'] == 1]
    today2 = db[db['forecast'] == 2]
    today3 = db[db['forecast'] == 3]
    today4 = db[db['forecast'] == 4]
    today5 = db[db['forecast'] == 5]
    today6 = db[db['forecast'] == 6]

    # Dataframe for Today + Forecast
    tf = pd.DataFrame(None)
    tf['today+0'] = today0['temp_max'].reset_index(drop=True)
    tf['today+1'] = today1['temp_max'].reset_index(drop=True)
    tf['today+2'] = today2['temp_max'].reset_index(drop=True)
    tf['today+3'] = today3['temp_max'].reset_index(drop=True)
    tf['today+4'] = today4['temp_max'].reset_index(drop=True)
    tf['today+5'] = today5['temp_max'].reset_index(drop=True)
    tf['today+6'] = today6['temp_max'].reset_index(drop=True)

    tf.index = dates_index # set the index to the dataframe.

    # Create Accuracy Table
    tf.index = pd.to_datetime(tf.index)  # Change the new index back into datetime.

    # Accuracy Mechanism: Compare forecast to actual Temp.
    fac = pd.DataFrame()
    counter = list(range(len(tf)))
    columns = list(tf.columns)

    for i in counter:
        # 7 day forecast inc today, so len can't exceed 7
        if i < 7:
            window = i
            j = i
        else:
            window = 6
            j = 6

        # Start date at most recent row
        actual_date = tf.index[-1]  # start with the last day
        window_date = actual_date - pd.DateOffset(
            days=window)  # Number of days in the past can't be more than those forecast
        row_0 = tf.index[0]  # We want to end when window date is equal to row_0.

        tf_list = []  # temporary holder of weeks values.
        while window_date >= row_0:
            true_temp = int(tf.loc[actual_date][0])  # True temperature recorded on day
            predicted_temp = int(tf.loc[window_date][window])  # data predicted on value of window
            difference = true_temp - predicted_temp
            # loop
            actual_date -= pd.DateOffset(days=1)  # take off 1 day.
            window_date -= pd.DateOffset(days=1)  # take off 1 day.
            # append
            tf_list.append(difference)
            # Add list to df as series
        fac[columns[j]] = pd.Series(tf_list[::-1])  # Add list backwards.

    tf.index = dates_index  # change the index back into string format
    fac.index = dates_index  # same index
    
    #################################
    # Persistence
    ################################

    # Persistence Mechanism subtract each max temp from the one before.
    pmodel = pd.Series([today - yesterday for today, yesterday in zip(tf['today+0'], tf['today+0'][1:])], index=tf.index[:len(tf.index)-1])

    # Assign pmodel vals to series.
    persistence = pd.DataFrame()
    persistence['Persistence Accuracy'] = pmodel.values
    for i in range(1, 7):
        persistence[str(i)+' Day Forecast'] = pd.Series(fac['today+'+str(i)].values)
    persistence.index = dates_index[:len(tf)-1]


    #################################
    # Save to file
    ################################

    tf.to_csv('./static/data/forecast_dataframe.csv')
    fac.to_csv('./static/data/accuracy_dataframe.csv')
    persistence.to_csv('./static/data/persistence_dataframe.csv')

    print('Forecast & Accuracy CSV Saved without errors.', '\n')
