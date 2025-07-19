import pandas as pd
import numpy as np
import json
import os
import warnings
warnings.filterwarnings('ignore')

from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet

def load_dataset(dataset_name):
    """Load dataset from input folder"""
    file_path = f"input/{dataset_name}.csv"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset {file_path} not found. Run data_generator.py first.")
    
    df = pd.read_csv(file_path)
    
    # Handle different date column names and formats
    date_columns = ['Date', 'Month', 'observation_date']
    date_col = None
    for col in date_columns:
        if col in df.columns:
            date_col = col
            break
    
    if date_col is None:
        raise ValueError(f"No date column found in {dataset_name}. Expected one of: {date_columns}")
    
    # Convert date column to datetime with special handling for shampoo format
    if dataset_name == 'shampoo_sales':
        # Handle "1-01" format (year-month)
        df[date_col] = df[date_col].astype(str)
        # Convert "1-01" to "2001-01-01" format
        df[date_col] = df[date_col].apply(lambda x: f"200{x.split('-')[0]}-{x.split('-')[1]}-01" if '-' in x else x)
    
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Get the value column (exclude date column)
    value_col = [col for col in df.columns if col != date_col][0]
    
    # Sort by date and return time series
    df = df.sort_values(date_col).reset_index(drop=True)
    return df[date_col], df[value_col].values

def forecast(train_data, vendor_name, n=12):
    """Generate forecasts using vendor-specific algorithms"""
    # Set random seed based on vendor name for reproducible but different results
    np.random.seed(hash(vendor_name) % 2**32)

    if vendor_name == 'AWS':
        # AWS uses ARIMA
        try:
            model = ARIMA(train_data, order=(1, 1, 1))
            fitted_model = model.fit()
            forecast_values = fitted_model.forecast(steps=n)
            
            # Add some AWS-specific noise
            forecast_values *= (1 + np.random.normal(0, 0.02, n))
            return forecast_values
        except Exception as e:
            print(f"ARIMA failed for AWS: {e}")
            return np.full(n, train_data[-1])
    
    elif vendor_name == 'Azure':
        # Azure uses Holt-Winters
        try:
            seasonal_periods = 12 if len(train_data) >= 24 else 4
            model = ExponentialSmoothing(train_data, seasonal_periods=seasonal_periods)
            fitted_model = model.fit()
            forecast_values = fitted_model.forecast(steps=n)
            
            # Add some Azure-specific bias
            forecast_values *= 0.99  # Slight downward bias
            return forecast_values
        except Exception as e:
            print(f"Holt-Winters failed for Azure: {e}")
            return np.full(n, np.mean(train_data[-3:]))
    
    elif vendor_name == 'Databricks':
        # Databricks uses Prophet
        try:
            dates = pd.date_range(start='2020-01-01', periods=len(train_data), freq='MS')
            df_prophet = pd.DataFrame({'ds': dates, 'y': train_data})
            
            model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
            model.fit(df_prophet)
            future = model.make_future_dataframe(periods=n, freq='MS')
            forecast_values = model.predict(future)['yhat'].iloc[-n:].values
            
            # Add some Databricks-specific trend
            trend_adjustment = np.linspace(0, 0.02, n)
            forecast_values *= (1 + trend_adjustment)
            return forecast_values
        except Exception as e:
            print(f"Prophet failed for Databricks: {e}")
            # Simple linear trend as fallback
            x = np.arange(len(train_data))
            p = np.poly1d(np.polyfit(x, train_data, 1))
            return p(np.arange(len(train_data), len(train_data) + n))
    
    else:
        # Fallback for unknown vendors
        return np.full(n, train_data[-1])

def main():
    with open('vendor_config.json') as f:
        config = json.load(f)

    os.makedirs('input', exist_ok=True)

    # Get list of datasets
    datasets = config.get('datasets', [])
    if not datasets:
        print("No datasets found in config. Please check vendor_config.json")
        return

    for vendor in config['vendors']:
        vendor_name = vendor['name']
        print(f"Generating forecasts for {vendor_name}...")
        
        files = vendor.get('forecast_files', {})

        for dataset_name, forecast_path in files.items():
            if dataset_name not in datasets:
                continue
                
            try:
                # Load the actual dataset
                dates, values = load_dataset(dataset_name)
                
                # Split data into train/test (use 80% for training)
                split_idx = int(len(values) * 0.8)
                train_data = values[:split_idx]
                test_data = values[split_idx:]
                test_dates = dates[split_idx:]
                
                # Generate forecast for the test period
                forecast_values = forecast(train_data, vendor_name, len(test_data))
                
                # Create forecast dataframe
                df_forecast = pd.DataFrame({
                    'Date': test_dates,
                    'Actual': test_data,
                    'Forecast': forecast_values.round(2)
                })

                # Save forecast
                os.makedirs(os.path.dirname(forecast_path), exist_ok=True)
                df_forecast.to_csv(forecast_path, index=False)
                print(f"  ✅ {dataset_name}: {len(test_data)} forecasts generated")
                
            except Exception as e:
                print(f"  ❌ {dataset_name}: {str(e)}")

    print("✅ All forecasts generated")

if __name__ == "__main__":
    main()