import pandas as pd
from fbprophet import Prophet  # Timeseries Forecasting


def build_prophet_forecaster():
    training_data_path = './static/data/training_dataframe.csv'
    training_data = pd.read_csv(training_data_path, index_col=0)

    # Prediction DataFrame
    historical_data = pd.DataFrame(None)
    historical_data['ds'] = training_data.index  # Create our date column
    historical_data['y'] = training_data['max_temp_c'].values  # Using previous Max-temp data to forecast

    historical_data.index = pd.to_datetime(historical_data['ds'])
    historical_data['ds'] = historical_data.index

    # grab the new data
    forecast_data = pd.read_csv('./static/data/forecast_dataframe.csv', index_col=0)
    forecast_data['ds'] = forecast_data.index
    forecast_data['y'] = forecast_data[['today+0']].astype(float)
    forecast_data = forecast_data[['ds', 'y']]

    model_data = pd.concat([historical_data, forecast_data], axis=0)

    # Forecast Data
    model = Prophet(
        changepoint_prior_scale=.75,
        growth='linear',
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False)  # no weekly seasonality in weather!
    model.fit(model_data)

    future = model.make_future_dataframe(periods=6)  # forecast 6 days beyond available data.
    forecast = model.predict(future)  # predict function
    # Plot figures
    model.plot(forecast, xlabel='Date', ylabel='Temperature').savefig('./static/charts/forecast.png');
    model.plot_components(forecast).savefig('./static/charts/components.png');
    print('Prophet images saved')

    # Build dataframe of latest predictions.
    prophet_forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]  # show the dataframe.
    prophet_forecast.reset_index(drop=True, inplace=True)

    # save to file
    prophet_forecast.tail(6).to_csv('./static/data/prophet_dataframe.csv')

    print('Prophet Forecaster Saved CSV without errors.', '\n')
