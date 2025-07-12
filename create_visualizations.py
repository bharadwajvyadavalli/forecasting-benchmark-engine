"""
Create visualizations for benchmark results
"""
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def load_results():
    """Load benchmark results"""
    with open('output/benchmark_results.json', 'r') as f:
        return json.load(f)


def create_metrics_comparison():
    """Create bar chart comparing metrics across vendors"""
    results = load_results()

    # Prepare data for visualization
    metrics_data = []
    for vendor_name, vendor_data in results['vendors'].items():
        for dataset, dataset_data in vendor_data.items():
            if 'metrics' in dataset_data:
                for metric, value in dataset_data['metrics'].items():
                    metrics_data.append({
                        'Vendor': vendor_name,
                        'Dataset': dataset,
                        'Metric': metric,
                        'Value': value
                    })

    df = pd.DataFrame(metrics_data)

    # Create subplots for each metric
    metrics = ['MAE', 'MAPE', 'WAPE', 'RMSE']
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.ravel()

    for i, metric in enumerate(metrics):
        metric_df = df[df['Metric'] == metric]
        pivot_df = metric_df.pivot(index='Dataset', columns='Vendor', values='Value')

        ax = axes[i]
        pivot_df.plot(kind='bar', ax=ax)
        ax.set_title(f'{metric} by Dataset and Vendor')
        ax.set_xlabel('Dataset')
        ax.set_ylabel(metric)
        ax.legend(title='Vendor')
        ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig('output/metrics_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()


def create_vendor_heatmap():
    """Create heatmap of vendor performance"""
    results = load_results()

    # Create matrix of MAPE values
    vendors = list(results['vendors'].keys())
    datasets = list(results['summary'].keys())
    if 'overall_best' in datasets:
        datasets.remove('overall_best')

    mape_matrix = []
    for vendor in vendors:
        row = []
        for dataset in datasets:
            if dataset in results['vendors'][vendor] and 'metrics' in results['vendors'][vendor][dataset]:
                row.append(results['vendors'][vendor][dataset]['metrics']['MAPE'])
            else:
                row.append(np.nan)
        mape_matrix.append(row)

    # Create heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(mape_matrix,
                xticklabels=datasets,
                yticklabels=vendors,
                annot=True,
                fmt='.1f',
                cmap='RdYlGn_r',
                cbar_kws={'label': 'MAPE (%)'},
                vmin=0,
                vmax=20)

    plt.title('Vendor Performance Heatmap (MAPE %)')
    plt.xlabel('Dataset')
    plt.ylabel('Vendor')
    plt.tight_layout()
    plt.savefig('output/vendor_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()


def create_summary_chart():
    """Create summary comparison chart"""
    results = load_results()

    # Calculate average metrics per vendor
    vendor_summary = {}
    for vendor_name, vendor_data in results['vendors'].items():
        metrics_sum = {'MAE': [], 'MAPE': [], 'WAPE': [], 'RMSE': []}

        for dataset_data in vendor_data.values():
            if 'metrics' in dataset_data:
                for metric in metrics_sum:
                    metrics_sum[metric].append(dataset_data['metrics'][metric])

        vendor_summary[vendor_name] = {
            metric: np.mean(values) for metric, values in metrics_sum.items()
        }

    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))

    vendors = list(vendor_summary.keys())
    x = np.arange(len(vendors))
    width = 0.2

    metrics = ['MAE', 'MAPE', 'WAPE', 'RMSE']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for i, metric in enumerate(metrics):
        values = [vendor_summary[v][metric] for v in vendors]
        ax.bar(x + i * width, values, width, label=metric, color=colors[i])

    ax.set_xlabel('Vendor')
    ax.set_ylabel('Average Value')
    ax.set_title('Average Metrics by Vendor')
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(vendors)
    ax.legend()

    plt.tight_layout()
    plt.savefig('output/summary_chart.png', dpi=150, bbox_inches='tight')
    plt.close()


def main():
    print("Creating visualizations...")
    create_metrics_comparison()
    create_vendor_heatmap()
    create_summary_chart()
    print("✓ Visualizations saved to output/")


if __name__ == "__main__":
    main()