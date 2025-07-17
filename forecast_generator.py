import pandas as pd
import numpy as np
import json
import os
import warnings
warnings.filterwarnings('ignore')

from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet

def generate_data(vendor, dataset, months=36):
    np.random.seed(hash(f"{vendor}_{dataset}") % 2**32)
    dates = pd.date_range('2022-01-01', periods=months, freq='MS')
    base = 50000 + hash(vendor) % 30000 + hash(dataset) % 20000

    values = []
    for i in range(months):
        value = base * (1 + 0.02) ** (i / 12)  # trend
        value *= 1 + 0.1 * np.sin(2 * np.pi * i / 12)  # seasonality
        value *= 1 + np.random.normal(0, 0.05)  # noise
        values.append(value)

    return dates, np.array(values)

def forecast(train_data, n=12):
    forecasts = []

    # ARIMA
    try:
        forecasts.append(ARIMA(train_data, order=(1,1,1)).fit().forecast(steps=n))
    except:
        forecasts.append(np.full(n, train_data[-1]))

    # Holt-Winters
    try:
        forecasts.append(ExponentialSmoothing(train_data, seasonal_periods=12).fit().forecast(steps=n))
    except:
        forecasts.append(np.full(n, np.mean(train_data[-3:])))

    # Prophet
    try:
        df = pd.DataFrame({'ds': pd.date_range('2022-01-01', periods=len(train_data), freq='MS'), 'y': train_data})
        m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
        m.fit(df)
        future = m.make_future_dataframe(periods=n, freq='MS')
        forecasts.append(m.predict(future)['yhat'].iloc[-n:].values)
    except:
        x = np.arange(len(train_data))
        p = np.poly1d(np.polyfit(x, train_data, 1))
        forecasts.append(p(np.arange(len(train_data), len(train_data) + n)))

    return np.mean(forecasts, axis=0)

def main():
    with open('vendor_config.json') as f:
        config = json.load(f)

    os.makedirs('input', exist_ok=True)

    for vendor in config['vendors']:
        files = vendor.get('forecast_files', {'single': vendor.get('forecast_file')})

        for dataset, path in files.items():
            dates, values = generate_data(vendor['name'], dataset)
            train, test = values[:24], values[24:]

            df = pd.DataFrame({
                'Date': dates[24:],
                'Actual': test.round(2),
                'Forecast': forecast(train, len(test)).round(2)
            })

            os.makedirs(os.path.dirname(path), exist_ok=True)
            df.to_csv(path, index=False)

    print("✅ Forecasts generated")

if __name__ == "__main__":
    main()