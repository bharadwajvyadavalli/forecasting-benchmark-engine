# Forecasting Benchmark Engine

Advanced tool to benchmark forecast accuracy across vendors using multiple real-world datasets and sophisticated metrics.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate datasets
python data_generator.py

# Run the complete benchmark pipeline
python run_all.py
```

## Datasets

The system uses 5 diverse time series datasets:

1. **Monthly Car Sales** - Automotive industry data (108 records)
2. **US Auto Inventory (AUINSA)** - Federal Reserve Economic Data (389 records)
3. **Sunspots** - Astronomical data with 11-year solar cycles (realistic simulation)
4. **Shampoo Sales** - Consumer goods time series (36 records)
5. **Air Passengers** - Transportation data (144 records)

All datasets are automatically downloaded and stored in the `input/` folder.

## Files

- **data_generator.py** - Downloads and prepares datasets from multiple sources
- **forecast_generator.py** - Generates forecasts using ARIMA, Holt-Winters, and Prophet
- **metrics_calculator.py** - Calculates advanced metrics (Bias, CRPS, Anomaly%, Drift, TP-F1)
- **visualization_generator.py** - Creates detailed charts and metrics table
- **dashboard_creator.py** - Generates interactive HTML dashboard
- **run_all.py** - Orchestrates the complete pipeline
- **vendor_config.json** - Configuration for vendor forecast file paths

## Output

- **output/dashboard.html** - Interactive dashboard (open in browser)
- **output/metrics_comparison.png** - Average metrics by vendor
- **output/dataset_details.png** - All metrics breakdown by dataset
- **output/metrics_table.png** - Detailed statistics (min/max/avg/std)
- **output/metrics_heatmap.png** - Performance heatmap across all datasets

## Metrics

| Metric | Description | Better When |
|--------|-------------|-------------|
| Bias | Average forecast error | Near 0 |
| CRPS | Continuous Ranked Probability Score | Lower |
| Anomaly% | Percentage of outlier residuals | Lower |
| Drift | Data distribution changes | Lower |
| TP-F1 | Turning point detection accuracy | Higher |

## Vendors Supported

Each vendor uses a different forecasting algorithm:

- **AWS** - ARIMA (AutoRegressive Integrated Moving Average)
  - Good for trend and seasonality patterns
  - Handles non-stationary time series well
  
- **Azure** - Holt-Winters Exponential Smoothing
  - Excellent for seasonal patterns
  - Simple and interpretable
  
- **Databricks** - Prophet
  - Robust for trend changes and holiday effects
  - Handles missing data and outliers well

Each vendor's forecasts are compared across all 5 datasets using the same evaluation framework, allowing for direct algorithm comparison.