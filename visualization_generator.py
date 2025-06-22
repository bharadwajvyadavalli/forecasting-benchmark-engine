"""
Module for generating visualization charts dynamically based on vendor data
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import sys
import numpy as np

def setup_plot_style():
    """Set up consistent plot styling"""
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'

def load_vendor_config():
    """Load vendor configuration from JSON file"""
    try:
        with open('vendor_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: vendor_config.json not found!")
        sys.exit(1)

def create_metrics_comparison_chart(vendor_metrics):
    """Create bar chart comparing metrics across vendors"""
    # Dynamic sizing based on number of vendors
    n_vendors = len(vendor_metrics)
    fig_width = max(10, n_vendors * 2)

    fig, ax = plt.subplots(figsize=(fig_width, 6))

    # Convert to DataFrame for easier plotting
    metrics_df = pd.DataFrame(vendor_metrics).T

    # Select key metrics for comparison
    key_metrics = ['MAE', 'MAPE', 'WAPE', 'RMSE']
    metrics_to_plot = metrics_df[key_metrics]

    # Create bar chart
    x = np.arange(len(metrics_to_plot.index))
    width = 0.2

    for i, metric in enumerate(key_metrics):
        offset = (i - len(key_metrics)/2 + 0.5) * width
        bars = ax.bar(x + offset, metrics_to_plot[metric], width, label=metric)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=8)

    # Customize chart
    ax.set_title('Forecast Accuracy Metrics by Vendor', fontsize=16, pad=20)
    ax.set_xlabel('Vendor', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_to_plot.index, rotation=45 if n_vendors > 5 else 0)
    ax.legend(title='Metrics', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig('output/metrics_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()

def create_time_series_plots(all_forecasts):
    """Create time series plots for each vendor"""
    n_vendors = len(all_forecasts)

    # Dynamic layout based on number of vendors
    if n_vendors <= 3:
        fig, axes = plt.subplots(n_vendors, 1, figsize=(12, 4*n_vendors))
    else:
        cols = 2
        rows = (n_vendors + 1) // 2
        fig, axes = plt.subplots(rows, cols, figsize=(14, 4*rows))
        axes = axes.flatten()

    if n_vendors == 1:
        axes = [axes]

    # Use a color palette
    colors = plt.cm.tab10(np.linspace(0, 1, n_vendors))

    for idx, (vendor, df) in enumerate(sorted(all_forecasts.items())):
        ax = axes[idx]

        # Plot actual and forecast
        ax.plot(df['Date'], df['Actual'], label='Actual',
                linewidth=2, color=colors[idx])
        ax.plot(df['Date'], df['Forecast'], label='Forecast',
                linewidth=2, linestyle='--', color=colors[idx], alpha=0.7)

        # Add a shaded area between actual and forecast
        ax.fill_between(df['Date'], df['Actual'], df['Forecast'],
                       alpha=0.2, color=colors[idx])

        # Customize subplot
        ax.set_title(f'{vendor} - Actual vs Forecast', fontsize=14, pad=10)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Value ($)', fontsize=11)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)

        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Rotate x-axis labels
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Hide extra subplots if using grid layout
    if n_vendors > 3 and n_vendors % 2 != 0:
        axes[-1].set_visible(False)

    plt.tight_layout()
    plt.savefig('output/time_series_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()

def create_error_distribution_chart(all_forecasts):
    """Create histogram of forecast errors"""
    fig, ax = plt.subplots(figsize=(10, 6))

    n_vendors = len(all_forecasts)
    colors = plt.cm.tab10(np.linspace(0, 1, n_vendors))

    all_errors = []

    for idx, (vendor, df) in enumerate(sorted(all_forecasts.items())):
        # Calculate percentage error
        error_pct = ((df['Forecast'] - df['Actual']) / df['Actual']) * 100
        all_errors.extend(error_pct)

        # Plot histogram
        ax.hist(error_pct, bins=20, alpha=0.6, label=vendor,
                color=colors[idx], edgecolor='black', linewidth=0.5)

    # Add statistics
    mean_error = np.mean(all_errors)
    std_error = np.std(all_errors)

    # Customize chart
    ax.set_title(f'Forecast Error Distribution\n(μ={mean_error:.2f}%, σ={std_error:.2f}%)',
                 fontsize=16, pad=20)
    ax.set_xlabel('Error Percentage (%)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add vertical lines
    ax.axvline(x=0, color='red', linestyle='--', alpha=0.5, label='Zero Error')
    ax.axvline(x=mean_error, color='green', linestyle='--', alpha=0.5, label='Mean Error')

    plt.tight_layout()
    plt.savefig('output/error_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()

def create_performance_heatmap(vendor_metrics):
    """Create heatmap of normalized metrics"""
    # Dynamic sizing based on number of vendors
    n_vendors = len(vendor_metrics)
    fig_height = max(6, n_vendors * 0.8)

    fig, ax = plt.subplots(figsize=(10, fig_height))

    # Convert to DataFrame
    metrics_df = pd.DataFrame(vendor_metrics).T

    # Select metrics for heatmap
    heatmap_metrics = ['MAE', 'MAPE', 'WAPE', 'RMSE', 'SMAPE']
    available_metrics = [m for m in heatmap_metrics if m in metrics_df.columns]
    metrics_for_heatmap = metrics_df[available_metrics]

    # Normalize metrics (lower is better for all metrics)
    normalized_df = metrics_for_heatmap.copy()
    for col in metrics_for_heatmap.columns:
        max_val = metrics_for_heatmap[col].max()
        if max_val != 0:
            normalized_df[col] = 1 - (metrics_for_heatmap[col] / max_val)
        else:
            normalized_df[col] = 1

    # Create heatmap
    sns.heatmap(normalized_df, annot=True, fmt='.2f', cmap='RdYlGn',
                center=0.5, vmin=0, vmax=1, cbar_kws={'label': 'Performance Score'},
                linewidths=0.5)

    ax.set_title('Vendor Performance Heatmap\n(Higher values = Better performance)',
                 fontsize=14, pad=20)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    plt.tight_layout()
    plt.savefig('output/performance_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()

def create_forecast_accuracy_over_time(all_forecasts):
    """Create line chart showing forecast accuracy over time"""
    fig, ax = plt.subplots(figsize=(12, 6))

    n_vendors = len(all_forecasts)
    colors = plt.cm.tab10(np.linspace(0, 1, n_vendors))

    for idx, (vendor, df) in enumerate(sorted(all_forecasts.items())):
        # Calculate rolling MAPE (3-month window)
        df['APE'] = np.abs((df['Forecast'] - df['Actual']) / df['Actual']) * 100
        df['Rolling_MAPE'] = df['APE'].rolling(window=3, min_periods=1).mean()

        # Plot rolling MAPE
        ax.plot(df['Date'], df['Rolling_MAPE'], label=vendor,
                linewidth=2, color=colors[idx])

    # Customize chart
    ax.set_title('Forecast Accuracy Over Time (3-Month Rolling MAPE)', fontsize=16, pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('MAPE (%)', fontsize=12)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)

    # Rotate x-axis labels
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig('output/accuracy_over_time.png', dpi=150, bbox_inches='tight')
    plt.close()

def load_all_forecasts(vendor_config):
    """Load forecast data for all vendors"""
    all_forecasts = {}

    for vendor_info in vendor_config.get('vendors', []):
        vendor_name = vendor_info.get('name')
        file_path = vendor_info.get('forecast_file')

        if not vendor_name or not file_path:
            continue

        try:
            df = pd.read_csv(file_path, parse_dates=['Date'])
            all_forecasts[vendor_name] = df
        except Exception as e:
            print(f"   ⚠️  Warning: Could not load {file_path}: {str(e)}")
            continue

    return all_forecasts

def main():
    """Main function to generate all visualizations"""
    print("📈 Visualization Generator Module")
    print("=" * 50)

    # Create output directory
    os.makedirs('output', exist_ok=True)

    # Load vendor configuration
    print("\n📊 Loading vendor configuration...")
    vendor_config = load_vendor_config()

    # Load metrics
    print("📊 Loading metrics results...")
    try:
        with open('output/metrics_results.json', 'r') as f:
            metrics_data = json.load(f)
            vendor_metrics = metrics_data.get('metrics', {})
    except FileNotFoundError:
        print("❌ Error: metrics_results.json not found!")
        print("   Please run metrics_calculator.py first.")
        sys.exit(1)

    if not vendor_metrics:
        print("❌ Error: No metrics found in results!")
        sys.exit(1)

    # Load all forecast data
    print(f"\n📊 Loading forecast data for {len(vendor_config.get('vendors', []))} vendor(s)...")
    all_forecasts = load_all_forecasts(vendor_config)

    if not all_forecasts:
        print("❌ Error: No forecast data found!")
        sys.exit(1)

    print(f"   ✅ Loaded data for {len(all_forecasts)} vendor(s)")

    # Set up plot style
    setup_plot_style()

    # Generate visualizations
    print("\n🎨 Generating visualizations...")

    try:
        print("   📊 Creating metrics comparison chart...")
        create_metrics_comparison_chart(vendor_metrics)

        print("   📈 Creating time series plots...")
        create_time_series_plots(all_forecasts)

        print("   📊 Creating error distribution chart...")
        create_error_distribution_chart(all_forecasts)

        print("   🗺️  Creating performance heatmap...")
        create_performance_heatmap(vendor_metrics)

        print("   📈 Creating accuracy over time chart...")
        create_forecast_accuracy_over_time(all_forecasts)

        print("\n✅ Visualization generation completed!")
        print("📁 Charts saved to output/ folder:")
        print("   - metrics_comparison.png")
        print("   - time_series_comparison.png")
        print("   - error_distribution.png")
        print("   - performance_heatmap.png")
        print("   - accuracy_over_time.png")

    except Exception as e:
        print(f"\n❌ Error generating visualizations: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()