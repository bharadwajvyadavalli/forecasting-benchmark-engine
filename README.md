# Forecast Benchmarking Engine

A simple tool to benchmark forecast accuracy from multiple vendors (AWS, Azure, Databricks) across different datasets.

## Quick Start

1. Install dependencies:
```bash
pip install pandas numpy matplotlib seaborn

Run the benchmark:

bashpython run_benchmark.py

View results:


Open output/dashboard.html in your browser

Project Structure
├── vendor_config.json      # Configuration file
├── generate_sample_data.py # Generate test data
├── benchmark_engine.py     # Main analysis engine
├── create_visualizations.py # Generate charts
├── create_dashboard.py     # Generate HTML dashboard
├── run_benchmark.py        # Main runner script
├── input/                  # Forecast CSV files
│   └── [vendor]_[dataset]_forecast.csv
└── output/                 # Results
    ├── benchmark_results.json
    ├── dashboard.html
    └── *.png (charts)
Input Format
Each forecast CSV file should have:

Date: Date column
Actual: Actual values
Forecast: Forecasted values

Metrics Calculated

MAE: Mean Absolute Error
MAPE: Mean Absolute Percentage Error
WAPE: Weighted Absolute Percentage Error
RMSE: Root Mean Square Error
Bias: Average forecast bias

Adding New Vendors/Datasets
Edit vendor_config.json to add new vendors or datasets, then place the corresponding CSV files in the input/ folder.

---

## Summary

This simplified benchmarking engine:

1. **Loads forecast files** from AWS, Azure, and Databricks (already containing Actual vs Forecast)
2. **Calculates metrics** (MAE, MAPE, WAPE, RMSE, Bias)
3. **Creates visualizations** (comparison charts, heatmaps)
4. **Generates a dashboard** showing best performers

To use:
1. Copy all 7 files to PyCharm
2. Run `python run_benchmark.py`
3. Open `output/dashboard.html`

The system expects CSV files with Date, Actual, and Forecast columns. It will automatically generate sample data if none exists.