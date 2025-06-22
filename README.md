# Forecasting Benchmark Engine

A modular Python-based tool for benchmarking forecast accuracy across multiple vendors dynamically.

## Overview

This engine provides a flexible framework for analyzing forecast accuracy across any number of vendors. It reads vendor configurations from a JSON file, generates synthetic forecast data, calculates various accuracy metrics, creates visualizations, and produces an interactive HTML dashboard.

## Features

- **Dynamic Vendor Support**: Automatically detects and processes vendors from configuration file
- **Modular Architecture**: Separate modules for each functionality
- **Comprehensive Metrics**: Calculates MAE, MAPE, WAPE, RMSE, Bias, SMAPE, and Tracking Signal
- **Rich Visualizations**: Multiple chart types including time series, error distribution, and performance heatmap
- **Responsive Dashboard**: Modern HTML dashboard that adapts to any number of vendors
- **Flexible Configuration**: Easy to add or remove vendors via JSON configuration

## Project Structure

```
forecasting-benchmark-engine/
├── vendor_config.json       # Vendor configuration (user-created)
├── data_generator.py        # Module for generating synthetic data
├── metrics_calculator.py    # Module for calculating metrics
├── visualization_generator.py # Module for creating charts
├── dashboard_creator.py     # Module for HTML dashboard
├── input/                   # Input folder for forecast CSV files
│   └── [vendor]_forecast.csv files
├── output/                  # Output folder for results
│   ├── dashboard.html       # Main HTML dashboard
│   ├── metrics_results.json # Calculated metrics
│   ├── metrics_comparison.png
│   ├── time_series_comparison.png
│   ├── error_distribution.png
│   ├── performance_heatmap.png
│   └── accuracy_over_time.png
└── README.md               # This file
```

## Requirements

```bash
pip install pandas numpy matplotlib seaborn
```

## Setup

1. **Create vendor_config.json**:
   Create a `vendor_config.json` file in the project root with your vendor configuration:

   ```json
   {
     "vendors": [
       {
         "name": "AWS",
         "forecast_file": "input/aws_forecast.csv"
       },
       {
         "name": "Azure",
         "forecast_file": "input/azure_forecast.csv"
       },
       {
         "name": "Databricks",
         "forecast_file": "input/databricks_forecast.csv"
       }
     ]
   }
   ```

   You can add as many vendors as needed. The system will dynamically adapt to the number of vendors.

## Usage

Run each module in sequence:

### Step 1: Generate Forecast Data
```bash
python data_generator.py
```
- Reads vendor configuration from `vendor_config.json`
- Generates 24 months of synthetic forecast data for each vendor
- Creates CSV files in the `input/` folder

### Step 2: Calculate Metrics
```bash
python metrics_calculator.py
```
- Loads forecast data from CSV files
- Calculates accuracy metrics for each vendor
- Saves results to `output/metrics_results.json`
- Displays a summary table with all metrics

### Step 3: Create Visualizations
```bash
python visualization_generator.py
```
- Generates multiple charts:
  - Metrics comparison bar chart
  - Time series plots (actual vs forecast)
  - Error distribution histograms
  - Performance heatmap
  - Accuracy trend over time
- Saves PNG files to `output/` folder

### Step 4: Generate Dashboard
```bash
python dashboard_creator.py
```
- Creates an interactive HTML dashboard
- Automatically includes all available vendors and charts
- Highlights the best performing vendor
- Saves to `output/dashboard.html`

## Module Descriptions

### data_generator.py
- Generates synthetic forecast data with realistic patterns
- Uses vendor name hash for consistent but unique patterns
- Includes trends, seasonality, and random noise
- Automatically creates directories as needed

### metrics_calculator.py
- Calculates comprehensive accuracy metrics:
  - **MAE**: Mean Absolute Error
  - **MAPE**: Mean Absolute Percentage Error
  - **WAPE**: Weighted Absolute Percentage Error
  - **RMSE**: Root Mean Square Error
  - **Bias**: Average forecast bias
  - **SMAPE**: Symmetric Mean Absolute Percentage Error
  - **Tracking Signal**: Cumulative error indicator
- Identifies best performers for each metric

### visualization_generator.py
- Creates publication-quality visualizations
- Dynamically adjusts layouts based on number of vendors
- Uses color palettes that scale with vendor count
- Generates 5 different chart types

### dashboard_creator.py
- Produces a responsive HTML dashboard
- Dynamically adapts to available vendors and charts
- Modern design with gradient backgrounds
- Shows summary statistics and detailed metrics

## Adding New Vendors

To add new vendors:

1. Edit `vendor_config.json` and add new vendor entries:
   ```json
   {
     "name": "NewVendor",
     "forecast_file": "input/newvendor_forecast.csv"
   }
   ```

2. Run all modules in sequence starting from `data_generator.py`

The system will automatically:
- Generate data for the new vendor
- Calculate its metrics
- Include it in all visualizations
- Add it to the dashboard

## Customization

### Modifying Synthetic Data Parameters
In `data_generator.py`, you can adjust:
- Base values and growth rates
- Seasonality patterns
- Noise levels
- Time period (default: 24 months)

### Adding New Metrics
In `metrics_calculator.py`, add new metrics to the `calculate_metrics()` function.

### Changing Visualization Styles
In `visualization_generator.py`, modify plot styles, colors, and layouts.

## Output Files

- **vendor_config.json**: User-created vendor configuration
- **input/*.csv**: Generated or actual forecast data
- **output/metrics_results.json**: Calculated metrics with metadata
- **output/*.png**: Visualization charts
- **output/dashboard.html**: Interactive dashboard

## Notes

- The system is designed to handle any number of vendors
- All modules check for required files and provide helpful error messages
- Visualizations automatically scale and adjust to vendor count
- The dashboard works on both desktop and mobile devices

## Troubleshooting

If you encounter errors:

1. Ensure `vendor_config.json` exists and is valid JSON
2. Run modules in the correct order (1→2→3→4)
3. Check that required packages are installed
4. Verify file paths in vendor configuration are correct

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.