# import statements
import numpy as np
import pandas as pd

# Imputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

datafile_path = './static/data/training_dataframe.csv'
pickle_file_path = './static/data/training_dataframe.pkl'

# Note: These are the urls and default paths for future updates.
# The files may need to be downloaded at the same time so that they finish on the same day.
# min_temp_url = 'http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_display_type=dailyZippedDataFile&p_stn_num=086338&p_c=-1491037294&p_nccObsCode=123&p_startYear=2020'
# max_temp_url = 'http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_display_type=dailyZippedDataFile&p_stn_num=086338&p_c=-1491037098&p_nccObsCode=122&p_startYear=2020'
# rainfall = 'http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_display_type=dailyZippedDataFile&p_stn_num=086338&p_c=-1491039987&p_nccObsCode=136&p_startYear=2020'
# solar_exposure_url = 'http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_display_type=dailyZippedDataFile&p_stn_num=086338&p_c=-1491053811&p_nccObsCode=193&p_startYear=2020'
#
# rainfall_path = 'IDCJAC0009_086338_1800/IDCJAC0009_086338_1800_Data.csv'
# solar_exposure_path = 'IDCJAC0016_086338_1800/IDCJAC0016_086338_1800_Data.csv'
# temp_max_path = 'IDCJAC0010_086338_1800/IDCJAC0010_086338_1800_Data.csv'
# temp_min_path = 'IDCJAC0011_086338_1800/IDCJAC0011_086338_1800_Data.csv'


############
# Load Files
############

def load_data():
    temp_max = pd.read_csv('./static/data/training_data/temp_max.csv', infer_datetime_format=True, index_col=0)
    temp_min = pd.read_csv('./static/data/training_data/temp_min.csv', infer_datetime_format=True, index_col=0)
    rainfall = pd.read_csv('./static/data/training_data/rainfall.csv', infer_datetime_format=True, index_col=0)
    solar_exposure = pd.read_csv('./static/data/training_data/solar_exposure.csv', infer_datetime_format=True, index_col=0)
    print('Data loaded successfully', '\n')
    return temp_max, temp_min, rainfall, solar_exposure


def rainfall_eda(rainfall: int) -> pd.DataFrame:
    rainfall.columns = map(str.lower, rainfall.columns)  # Lower names
    rainfall.drop(['bureau of meteorology station number', 'period over which rainfall was measured (days)'], axis=1,
                  inplace=True)
    rainfall['date'] = pd.to_datetime(rainfall[['year', 'month', 'day']])
    rainfall.index = rainfall['date']  # set index as well.
    print('rainfall_eda complete')
    return rainfall


def temp_max_eda(temp_max: int) -> pd.DataFrame:
    temp_max.columns = map(str.lower, temp_max.columns)
    temp_max.drop(['bureau of meteorology station number', 'days of accumulation of maximum temperature'], axis=1,
                  inplace=True)
    temp_max['date'] = pd.to_datetime(temp_max[['year', 'month', 'day']])
    temp_max.index = temp_max['date']  # set index as well.
    print('temp_max_eda complete')
    return temp_max


def temp_min_eda(temp_min: int) -> pd.DataFrame:
    temp_min.columns = map(str.lower, temp_min.columns)
    temp_min.drop(['bureau of meteorology station number', 'days of accumulation of minimum temperature'], axis=1,
                  inplace=True)
    temp_min['date'] = pd.to_datetime(temp_min[['year', 'month', 'day']])
    temp_min.index = temp_min['date']  # set index as well.
    print('temp_min_eda complete')
    return temp_min


def solar_exposure_eda(solar_exposure: int) -> pd.DataFrame:
    solar_exposure.columns = map(str.lower, solar_exposure.columns)
    solar_exposure.drop(['bureau of meteorology station number'], axis=1, inplace=True)
    solar_exposure['date'] = pd.to_datetime(solar_exposure[['year', 'month', 'day']])
    solar_exposure.index = solar_exposure['date']  # set index as well.
    print('solar_exposure_eda complete')
    return solar_exposure


def weather_training_data_assembly(temp_max, temp_min, rainfall, solar_exposure: pd.DataFrame) -> pd.DataFrame:
    weather_training_data = pd.merge(solar_exposure, temp_max, how='left', left_index=True, right_index=True,
                                     suffixes=('_se', '_maxt'))
    weather_training_data = pd.merge(weather_training_data, temp_min, how='left', left_index=True, right_index=True,
                                     suffixes=('_maxt', '_mint'))
    weather_training_data = pd.merge(weather_training_data, rainfall, how='left', left_index=True, right_index=True,
                                     suffixes=('_w', '_rf'))
    weather_training_data = weather_training_data[
        ['rainfall amount (millimetres)', 'quality', 'minimum temperature (degree c)', 'quality_mint',
         'maximum temperature (degree c)', 'quality_maxt', 'daily global solar exposure (mj/m*m)']]
    weather_training_data.rename(columns={'quality': 'quality_rf'}, inplace=True)  # Rain quality needs an identifier
    weather_training_data['quality_rf'] = weather_training_data['quality_rf'].map(dict(Y=1, N=0))
    weather_training_data['quality_maxt'] = weather_training_data['quality_maxt'].map(dict(Y=1, N=0))
    weather_training_data['quality_mint'] = weather_training_data['quality_mint'].map(dict(Y=1, N=0))
    # Linear conversion of 'Global Exposure' 0-40 to 'UV index' 0-12 (This is not scentific.)
    weather_training_data['daily global solar exposure (mj/m*m)'] = [((i - 0) / (40 - 0)) * (12 - 0) + 0 for i in
                                                                     weather_training_data[
                                                                         'daily global solar exposure (mj/m*m)']]
    weather_training_data = weather_training_data[
        weather_training_data.index > '20130601']  # cutoff point. See EDA notebook.
    print('Training File Assembled', '\n')
    return weather_training_data


def data_imputer(weather_training_data: pd.DataFrame) -> pd.DataFrame:
    # This is experimental, but seems to work well.
    imp = IterativeImputer(max_iter=10, random_state=0)
    imp.fit(weather_training_data)
    IterativeImputer(random_state=0)
    X_test = weather_training_data
    imputed_weather_training_data = np.round(imp.transform(X_test))
    imputed_weather_training_data = pd.DataFrame(imputed_weather_training_data, columns=weather_training_data.columns,
                                                 index=weather_training_data.index)
    imputed_weather_training_data.columns = ['rainfall_mm', 'quality_rf', 'min_temp_c', 'quality_mint', 'max_temp_c',
                                             'quality_maxt', 'uv_index']
    print('Weather Data Imputed', '\n')
    return imputed_weather_training_data


##############
# Fit Pipeline
##############

def eda_pipe(temp_max, temp_min, rainfall, solar_exposure: pd.DataFrame) -> pd.DataFrame:  # pass data files
    rainfall_eda(rainfall)
    temp_max_eda(temp_max)
    temp_min_eda(temp_min)
    solar_exposure_eda(solar_exposure)
    print('All EDA complete', '\n')
    return temp_max, temp_min, rainfall, solar_exposure


##########################
# Serialization or Pickling
##########################

# def serialize(imputed_weather_training_data):
#     with open(pickle_file_path, 'wb') as f:
#         dill.dump(imputed_weather_training_data, f)
#         print('Training data serialized')


##########################
# Saving to CSV
##########################

def save_to_csv(imputed_weather_training_data: pd.DataFrame):
    imputed_weather_training_data.to_csv(datafile_path, index=True)  # Save to csv (db is too slow)
    print('Training data saved to file','\n')


#######
# Main
#######

def build_training_dataframe():
    temp_max, temp_min, rainfall, solar_exposure = load_data()
    eda_pipe(temp_max, temp_min, rainfall, solar_exposure)
    weather_training_data = weather_training_data_assembly(temp_max, temp_min, rainfall, solar_exposure)
    imputed_weather_training_data = data_imputer(weather_training_data)
    # serialize(imputed_weather_training_data)
    save_to_csv(imputed_weather_training_data)

    print('Training data is ready','\n')
