#import statements
import numpy as np
import pandas as pd

# Model
from sklearn.ensemble import RandomForestRegressor
# Build and Process Class
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

# Imputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

# SQL
import sqlalchemy
import os
import dotenv  # Protect db creds
dotenv.load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = sqlalchemy.create_engine(DATABASE_URL)

# Serialise Model
import dill

datafile_path = './weather.csv'
pickle_file_path = './WeatherPipe.pkl'


class WeatherPreprocessor(BaseEstimator, TransformerMixin):
    print('New WeatherPreprocessor Class initiated', '\n')

    def __init__(self):
        self.feature_names = []

        
    ############
    # Transform
    ############
    def transform(self, X, *args):
        print('starting transform')
        self.feature_names = X.columns
        print('transform complete')
        return X

    def fit(self, X, *args):
        print('fit complete', '\n')
        return self

############
# Load Files
############

def load_data():    
    temp_max = pd.read_csv('./training_data/temp_max.csv', infer_datetime_format=True, index_col=0)
    temp_min = pd.read_csv('./training_data/temp_min.csv', infer_datetime_format=True, index_col=0)
    rainfall = pd.read_csv('./training_data/rainfall.csv', infer_datetime_format=True, index_col=0)
    solar_exposure = pd.read_csv('./training_data/solar_exposure.csv', infer_datetime_format=True, index_col=0)
    print('load_data complete', '\n')
    
    rainfall.columns = map(str.lower, rainfall.columns)  # Lower names
    rainfall.drop(['bureau of meteorology station number', 'period over which rainfall was measured (days)'], axis=1, inplace=True)
    rainfall['date'] = pd.to_datetime(rainfall[['year', 'month', 'day']])
    rainfall.index = rainfall['date']  # set index as well.
    print('rainfall EDA complete')
    
    temp_max.columns = map(str.lower, temp_max.columns)
    temp_max.drop(['bureau of meteorology station number', 'days of accumulation of maximum temperature'], axis=1, inplace=True)
    temp_max['date'] = pd.to_datetime(temp_max[['year', 'month', 'day']])
    temp_max.index = temp_max['date']  # set index as well.
    print('temp_max EDA complete')
    
    temp_min.columns = map(str.lower, temp_min.columns)
    temp_min.drop(['bureau of meteorology station number', 'days of accumulation of minimum temperature'], axis=1, inplace=True)
    temp_min['date'] = pd.to_datetime(temp_min[['year', 'month', 'day']])
    temp_min.index = temp_min['date']  # set index as well.
    print('temp_min EDA complete')
    
    solar_exposure.columns = map(str.lower, solar_exposure.columns)
    solar_exposure.drop(['bureau of meteorology station number'], axis=1, inplace=True)
    solar_exposure['date'] = pd.to_datetime(solar_exposure[['year', 'month', 'day']])
    solar_exposure.index = solar_exposure['date']  # set index as well.
    print('solar_exposure EDA complete')
    
    weather = pd.merge(solar_exposure, temp_max, how='left', left_index=True, right_index=True, suffixes=('_se', '_maxt'))
    weather = pd.merge(weather, temp_min, how='left', left_index=True, right_index=True, suffixes=('_maxt', '_mint'))
    weather = pd.merge(weather, rainfall, how='left', left_index=True, right_index=True, suffixes=('_w', '_rf'))
    weather = weather[['rainfall amount (millimetres)', 'quality', 'minimum temperature (degree c)', 'quality_mint',  'maximum temperature (degree c)', 'quality_maxt', 'daily global solar exposure (mj/m*m)']]
    weather.rename(columns={'quality': 'quality_rf'}, inplace=True)  # Rain quality needs an identifier
    weather['quality_rf'] = weather['quality_rf'].map(dict(Y=1, N=0))
    weather['quality_maxt'] = weather['quality_maxt'].map(dict(Y=1, N=0))
    weather['quality_mint'] = weather['quality_mint'].map(dict(Y=1, N=0))
    # Linear conversion of 'Global Exposure' 0-40 to 'UV index' 0-12 (This is not scentific.)
    weather['daily global solar exposure (mj/m*m)'] = [((i - 0) / (40 - 0)) * (12 - 0) + 0 for i in weather['daily global solar exposure (mj/m*m)']]
    weather = weather[weather.index > '20130601']  # cutoff point.
    print('_weather_EDA complete')
    
    # This is experimental, but seems to work well.
    imp = IterativeImputer(max_iter=10, random_state=0)
    imp.fit(weather)
    IterativeImputer(random_state=0)
    X_test = weather
    imp_weather = np.round(imp.transform(X_test))
    imp_weather = pd.DataFrame(imp_weather, columns=weather.columns, index=weather.index)
    imp_weather.columns = ['rainfall_mm', 'quality_rf', 'min_temp_c', 'quality_mint', 'max_temp_c', 'quality_maxt', 'uv_index']
    print('_imputer complete')
    # Push to SQL Here.
    imp_weather.to_csv(datafile_path, index=False)  # Save to csv (db is too slow)
    print(f'Forecast saved to db')
    # Define X, y
    X = imp_weather.drop(['max_temp_c'], axis=1)
    y = imp_weather['max_temp_c']
    print('Xy complete', '\n')
    return X, y


##############
# Fit Pipeline
##############

def fit_pipe(X, y):  # pass data files
    tp = WeatherPreprocessor()
    print('WeatherPreprocessor defined')
    # Create RF model
    rf = RandomForestRegressor(max_depth=3, random_state=42)
    print('RandomForestRegressor defined')
    pipe = Pipeline(steps=[('tp', tp), ('rf', rf)])
    print('Pipeline defined')
    pipe.fit(X, y)  # Function to make X,y
    print('fit_pipe complete', '\n')
    return pipe


##########################
# Serialization or Pickling
##########################

def serialize(pipe):
    with open(pickle_file_path, 'wb') as f:
        dill.dump(pipe, f)
        print('dill dump complete', '\n')
        

######
# Main
######

def main():
    try:
        X, y = load_data()
        print('Stage 1 complete', '\n')
        pipe = fit_pipe(X, y)
        print('Stage 2 complete', '\n')
        serialize(pipe)
        print('Stage 3 complete')
        print('RF pipeline is trained and serialized')
    except Exception as err:
        print(err.args)
        exit


# Program Entry Point
if __name__ == '__main__':
    main()
