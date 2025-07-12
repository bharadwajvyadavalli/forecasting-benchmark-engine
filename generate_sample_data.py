"""
Generate sample forecast data for testing
"""
import pandas as pd
import numpy as np
import os
import json


def generate_forecast_data(vendor_name, dataset_name, periods=24):
    """Generate sample forecast data with actuals and forecasts"""
    dates = pd.date_range('2022-01-01', periods=periods, freq='MS')

    # Base patterns for different datasets
    if 'dataset1' in dataset_name:  # Low volatility
        base = 10000
        trend = np.linspace(0, 1000, periods)
        seasonal = 500 * np.sin(2 * np.pi * np.arange(periods) / 12)
        noise = np.random.normal(0, 100, periods)
    elif 'dataset2' in dataset_name:  # High volatility
        base = 5000
        trend = np.linspace(0, 2000, periods)
        seasonal = 1000 * np.sin(2 * np.pi * np.arange(periods) / 12)
        noise = np.random.normal(0, 500, periods)
    elif 'dataset3' in dataset_name:  # Seasonal
        base = 15000
        trend = np.linspace(0, 500, periods)
        seasonal = 3000 * np.sin(2 * np.pi * np.arange(periods) / 12)
        noise = np.random.normal(0, 200, periods)
    elif 'dataset4' in dataset_name:  # Trending
        base = 8000
        trend = np.linspace(0, 5000, periods)
        seasonal = 300 * np.sin(2 * np.pi * np.arange(periods) / 12)
        noise = np.random.normal(0, 150, periods)
    else:  # Intermittent
        base = 1000
        trend = np.linspace(0, 200, periods)
        seasonal = 100 * np.sin(2 * np.pi * np.arange(periods) / 12)
        noise = np.random.normal(0, 50, periods)
        # Add zeros for intermittent pattern
        zero_mask = np.random.random(periods) > 0.7

    # Generate actuals
    actuals = base + trend + seasonal + noise
    if 'dataset5' in dataset_name:
        actuals = actuals * zero_mask
    actuals = np.maximum(actuals, 0)  # Ensure non-negative

    # Generate forecasts with vendor-specific error patterns
    if vendor_name == 'AWS':
        error_factor = 0.05 + np.random.normal(0, 0.02)
    elif vendor_name == 'Azure':
        error_factor = 0.08 + np.random.normal(0, 0.03)
    else:  # Databricks
        error_factor = 0.06 + np.random.normal(0, 0.025)

    forecast_error = np.random.normal(0, actuals.std() * error_factor, periods)
    forecasts = actuals + forecast_error
    forecasts = np.maximum(forecasts, 0)

    return pd.DataFrame({
        'Date': dates,
        'Actual': actuals.round(2),
        'Forecast': forecasts.round(2)
    })


def main():
    """Generate all sample data files"""
    os.makedirs('input', exist_ok=True)

    with open('vendor_config.json', 'r') as f:
        config = json.load(f)

    print("Generating sample forecast data...")

    for vendor in config['vendors']:
        vendor_name = vendor['name']
        for dataset, filepath in vendor['forecast_files'].items():
            df = generate_forecast_data(vendor_name, dataset)
            df.to_csv(filepath, index=False)
            print(f"✓ Generated {filepath}")

    print("\nSample data generation complete!")


if __name__ == "__main__":
    main()