"""
Forecasting Benchmark Engine - Main Analysis Module
"""
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime


class BenchmarkEngine:
    def __init__(self, config_file='vendor_config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.results = {}

    def calculate_metrics(self, df):
        """Calculate forecast accuracy metrics"""
        actual = df['Actual']
        forecast = df['Forecast']

        # Basic metrics
        mae = np.mean(np.abs(actual - forecast))
        mape = np.mean(np.abs((actual - forecast) / actual)) * 100
        wape = np.sum(np.abs(actual - forecast)) / np.sum(actual) * 100
        rmse = np.sqrt(np.mean((actual - forecast) ** 2))
        bias = np.mean(forecast - actual)

        # Handle division by zero for MAPE
        mape = np.mean(np.abs((actual - forecast) / actual.replace(0, np.nan))) * 100

        return {
            'MAE': round(mae, 2),
            'MAPE': round(mape, 2),
            'WAPE': round(wape, 2),
            'RMSE': round(rmse, 2),
            'Bias': round(bias, 2)
        }

    def run_benchmark(self):
        """Run benchmark analysis for all vendors and datasets"""
        print("Running Forecast Benchmark Analysis...")
        print("=" * 50)

        self.results = {
            'vendors': {},
            'summary': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Process each vendor
        for vendor in self.config['vendors']:
            vendor_name = vendor['name']
            print(f"\nProcessing {vendor_name}...")

            self.results['vendors'][vendor_name] = {}

            # Process each dataset
            for dataset_key, filepath in vendor['forecast_files'].items():
                if os.path.exists(filepath):
                    df = pd.read_csv(filepath, parse_dates=['Date'])
                    metrics = self.calculate_metrics(df)

                    self.results['vendors'][vendor_name][dataset_key] = {
                        'metrics': metrics,
                        'records': len(df)
                    }

                    print(f"  ✓ {dataset_key}: MAPE={metrics['MAPE']}%")
                else:
                    print(f"  ✗ {dataset_key}: File not found - {filepath}")

        # Calculate summary statistics
        self._calculate_summary()

        # Save results
        os.makedirs('output', exist_ok=True)
        with open('output/benchmark_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        print("\nBenchmark complete! Results saved to output/benchmark_results.json")

    def _calculate_summary(self):
        """Calculate summary statistics across all vendors"""
        # Find best vendor for each dataset
        for dataset in self.config['datasets']:
            best_vendor = None
            best_mape = float('inf')

            for vendor_name, vendor_data in self.results['vendors'].items():
                if dataset in vendor_data and 'metrics' in vendor_data[dataset]:
                    mape = vendor_data[dataset]['metrics']['MAPE']
                    if mape < best_mape:
                        best_mape = mape
                        best_vendor = vendor_name

            self.results['summary'][dataset] = {
                'best_vendor': best_vendor,
                'best_mape': best_mape
            }

        # Overall best vendor
        vendor_avg_mape = {}
        for vendor_name, vendor_data in self.results['vendors'].items():
            mapes = []
            for dataset_data in vendor_data.values():
                if 'metrics' in dataset_data:
                    mapes.append(dataset_data['metrics']['MAPE'])
            if mapes:
                vendor_avg_mape[vendor_name] = np.mean(mapes)

        if vendor_avg_mape:
            best_overall = min(vendor_avg_mape.items(), key=lambda x: x[1])
            self.results['summary']['overall_best'] = {
                'vendor': best_overall[0],
                'avg_mape': round(best_overall[1], 2)
            }


def main():
    engine = BenchmarkEngine()
    engine.run_benchmark()


if __name__ == "__main__":
    main()