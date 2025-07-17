# Forecasting Benchmark

Simple tool to benchmark forecast accuracy across vendors using advanced metrics.

## Quick Start

```bash
# Install dependencies
pip install pandas numpy matplotlib seaborn scipy scikit-learn statsmodels prophet

# Run everything
python run_all.py
```

## Files

- **forecast_generator.py** - Generates forecasts (ARIMA, Holt-Winters, Prophet)
- **metrics_calculator.py** - Calculates metrics (Bias, CRPS, Anomaly%, Drift, TP-F1)
- **visualization_generator.py** - Creates detailed charts and metrics table
- **dashboard_creator.py** - Generates HTML dashboard
- **run_all.py** - Runs everything

## Output

- **output/dashboard.html** - Open this in your browser
- **output/metrics_comparison.png** - Average metrics by vendor
- **output/dataset_details.png** - All metrics breakdown by dataset
- **output/metrics_table.png** - Detailed statistics (min/max/avg/std) for all metrics
- **output/metrics_heatmap.png** - Heatmap showing all metrics across all datasets

## Metrics

| Metric | Measures | Better |
|--------|----------|--------|
| Bias | Average error | Near 0 |
| CRPS | Probabilistic accuracy | Lower |
| Anomaly% | Outliers | Lower |
| Drift | Distribution change | Lower |
| TP-F1 | Trend detection | Higher |