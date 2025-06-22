"""
Module for calculating forecast accuracy metrics dynamically for all vendors
"""
import pandas as pd
import numpy as np
import json
import os
import sys

def load_vendor_config():
    """Load vendor configuration from JSON file"""
    try:
        with open('vendor_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: vendor_config.json not found!")
        print("   Please ensure vendor_config.json exists in the current directory.")
        sys.exit(1)

def calculate_metrics(df):
    """Calculate forecast accuracy metrics"""
    actual = df['Actual']
    forecast = df['Forecast']

    # MAE - Mean Absolute Error
    mae = np.mean(np.abs(actual - forecast))

    # MAPE - Mean Absolute Percentage Error
    mape = np.mean(np.abs((actual - forecast) / actual)) * 100

    # WAPE - Weighted Absolute Percentage Error
    wape = np.sum(np.abs(actual - forecast)) / np.sum(actual) * 100

    # RMSE - Root Mean Square Error
    rmse = np.sqrt(np.mean((actual - forecast) ** 2))

    # Bias
    bias = np.mean(forecast - actual)

    # Additional metrics
    # SMAPE - Symmetric Mean Absolute Percentage Error
    smape = np.mean(2 * np.abs(forecast - actual) / (np.abs(actual) + np.abs(forecast))) * 100

    # Tracking Signal (cumulative forecast error / MAE)
    cumulative_error = np.sum(forecast - actual)
    tracking_signal = cumulative_error / mae if mae != 0 else 0

    return {
        'MAE': round(mae, 2),
        'MAPE': round(mape, 2),
        'WAPE': round(wape, 2),
        'RMSE': round(rmse, 2),
        'Bias': round(bias, 2),
        'SMAPE': round(smape, 2),
        'Tracking_Signal': round(tracking_signal, 2)
    }

def load_forecast_data(file_path):
    """Load forecast data from CSV file"""
    try:
        df = pd.read_csv(file_path, parse_dates=['Date'])

        # Validate required columns
        required_columns = ['Date', 'Actual', 'Forecast']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"   ⚠️  Warning: Missing columns {missing_columns} in {file_path}")
            return None

        return df
    except Exception as e:
        print(f"   ⚠️  Error loading {file_path}: {str(e)}")
        return None

def save_metrics(vendor_metrics):
    """Save metrics to JSON file"""
    os.makedirs('output', exist_ok=True)

    output_data = {
        'metrics': vendor_metrics,
        'metadata': {
            'total_vendors': len(vendor_metrics),
            'best_performer_mape': min(vendor_metrics.items(), key=lambda x: x[1]['MAPE'])[0] if vendor_metrics else None,
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }

    with open('output/metrics_results.json', 'w') as f:
        json.dump(output_data, f, indent=2)

def print_metrics_summary(vendor_metrics):
    """Print formatted metrics summary"""
    if not vendor_metrics:
        print("\n❌ No metrics calculated!")
        return

    print("\n" + "="*80)
    print("FORECAST ACCURACY METRICS SUMMARY")
    print("="*80)

    # Create header
    headers = ['Vendor', 'MAE', 'MAPE (%)', 'WAPE (%)', 'RMSE', 'Bias', 'SMAPE (%)', 'Track.Sig']
    col_widths = [15, 10, 10, 10, 10, 10, 10, 10]

    # Print header
    header_line = ""
    for header, width in zip(headers, col_widths):
        header_line += f"{header:<{width}}"
    print(header_line)
    print("-" * 80)

    # Print metrics for each vendor
    for vendor, metrics in sorted(vendor_metrics.items()):
        row = f"{vendor:<15}"
        row += f"{metrics['MAE']:<10.2f}"
        row += f"{metrics['MAPE']:<10.2f}"
        row += f"{metrics['WAPE']:<10.2f}"
        row += f"{metrics['RMSE']:<10.2f}"
        row += f"{metrics['Bias']:<10.2f}"
        row += f"{metrics['SMAPE']:<10.2f}"
        row += f"{metrics['Tracking_Signal']:<10.2f}"
        print(row)

    # Find best performers
    print("\n" + "="*80)
    print("PERFORMANCE SUMMARY")
    print("="*80)

    best_mape = min(vendor_metrics.items(), key=lambda x: x[1]['MAPE'])
    best_wape = min(vendor_metrics.items(), key=lambda x: x[1]['WAPE'])
    best_rmse = min(vendor_metrics.items(), key=lambda x: x[1]['RMSE'])

    print(f"🏆 Best MAPE: {best_mape[0]} ({best_mape[1]['MAPE']}%)")
    print(f"🏆 Best WAPE: {best_wape[0]} ({best_wape[1]['WAPE']}%)")
    print(f"🏆 Best RMSE: {best_rmse[0]} (${best_rmse[1]['RMSE']:,.2f})")

def main():
    """Main function to calculate metrics for all vendors"""
    print("🧮 Metrics Calculator Module")
    print("=" * 50)

    # Load vendor configuration
    print("\n📊 Loading vendor configuration...")
    vendor_config = load_vendor_config()

    vendors = vendor_config.get('vendors', [])
    if not vendors:
        print("❌ Error: No vendors found in configuration!")
        sys.exit(1)

    # Calculate metrics for each vendor
    vendor_metrics = {}
    successful_calculations = 0

    print(f"\n📊 Processing {len(vendors)} vendor(s)...")

    for vendor_info in vendors:
        vendor_name = vendor_info.get('name')
        file_path = vendor_info.get('forecast_file')

        if not vendor_name or not file_path:
            print(f"   ⚠️  Skipping invalid vendor entry: {vendor_info}")
            continue

        # Load data
        df = load_forecast_data(file_path)

        if df is not None:
            # Calculate metrics
            metrics = calculate_metrics(df)
            vendor_metrics[vendor_name] = metrics
            print(f"   ✅ Calculated metrics for {vendor_name}")
            successful_calculations += 1
        else:
            print(f"   ❌ Failed to process {vendor_name}")

    if vendor_metrics:
        # Save metrics
        save_metrics(vendor_metrics)
        print(f"\n📁 Metrics saved to output/metrics_results.json")

        # Print summary
        print_metrics_summary(vendor_metrics)

        print(f"\n✅ Successfully processed {successful_calculations}/{len(vendors)} vendors")
    else:
        print("\n❌ No metrics could be calculated!")
        print("   Please ensure forecast files exist and contain valid data.")

if __name__ == "__main__":
    main()