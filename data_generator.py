"""
Module for generating synthetic forecast data for vendors specified in vendor_config.json
"""
import pandas as pd
import numpy as np
import os
import json
import sys

def load_vendor_config():
    """Load vendor configuration from JSON file"""
    try:
        with open('vendor_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: vendor_config.json not found!")
        print("   Please create a vendor_config.json file with vendor details.")
        print("\n📝 Example vendor_config.json:")
        print(json.dumps({
            "vendors": [
                {"name": "AWS", "forecast_file": "input/aws_forecast.csv"},
                {"name": "Azure", "forecast_file": "input/azure_forecast.csv"}
            ]
        }, indent=2))
        sys.exit(1)

def generate_synthetic_data(vendor_name, start_date='2023-07-01', months=24):
    """Generate synthetic forecast data for a vendor"""
    dates = pd.date_range(start=start_date, periods=months, freq='MS')

    # Dynamic base values based on vendor name hash
    # This ensures consistent values for same vendor names
    base_value = 50000 + (hash(vendor_name) % 50000)
    growth_rate = 0.015 + (hash(vendor_name) % 20) * 0.001

    # Generate actuals with trend and seasonality
    actuals = []
    forecasts = []

    for i in range(months):
        # Trend component
        trend = base_value * (1 + growth_rate) ** i

        # Seasonal component (stronger in Q4)
        month = dates[i].month
        seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * month / 12) + 0.05 * (month in [10, 11, 12])

        # Random noise
        noise = np.random.normal(0, 0.05)

        actual = trend * seasonal_factor * (1 + noise)

        # Forecast with some error (vendor-specific error pattern)
        error_base = 0.06 + (hash(vendor_name) % 5) * 0.01
        forecast_error = np.random.normal(0, error_base)
        forecast = actual * (1 + forecast_error)

        actuals.append(actual)
        forecasts.append(forecast)

    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Actual': actuals,
        'Forecast': forecasts
    })

    # Round values
    df['Actual'] = df['Actual'].round(2)
    df['Forecast'] = df['Forecast'].round(2)

    return df

def main():
    """Main function to generate data for all vendors"""
    print("🚀 Data Generator Module")
    print("=" * 50)

    # Create input directory
    os.makedirs('input', exist_ok=True)

    # Load vendor configuration
    print("\n📝 Loading vendor configuration...")
    vendor_config = load_vendor_config()

    vendors = vendor_config.get('vendors', [])
    if not vendors:
        print("❌ Error: No vendors found in configuration!")
        sys.exit(1)

    print(f"   ✅ Found {len(vendors)} vendor(s) in configuration")

    # Generate data for each vendor
    print("\n📊 Generating synthetic forecast data...")
    generated_count = 0

    for vendor_info in vendors:
        vendor_name = vendor_info.get('name')
        file_path = vendor_info.get('forecast_file')

        if not vendor_name or not file_path:
            print(f"   ⚠️  Skipping invalid vendor entry: {vendor_info}")
            continue

        # Create directory if needed
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # Generate data
        df = generate_synthetic_data(vendor_name)

        # Save to CSV
        df.to_csv(file_path, index=False)
        print(f"   ✅ Generated {file_path} for {vendor_name}")
        generated_count += 1

    print(f"\n✅ Data generation completed!")
    print(f"📁 Generated {generated_count} forecast file(s) in the input folder")

if __name__ == "__main__":
    main()