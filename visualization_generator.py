import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np


def main():
    with open('output/metrics_results.json') as f:
        results = json.load(f)

    dataset_names = {
        'monthly_car_sales': 'Car Sales',
        'us_auto_inventory': 'Auto Inventory',
        'sunspots': 'Sunspots',
        'shampoo_sales': 'Shampoo Sales',
        'air_passengers': 'Air Passengers'
    }

    vendors = list(results.keys())
    metrics = ['Bias', 'CRPS', 'Residual_Anomaly_%', 'Data_Drift', 'Turning_Point_F1']

    # 1. Metrics Comparison
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, metric in enumerate(metrics):
        ax = axes[i]
        values = [results[v]['average'][metric] for v in vendors]
        colors = ['#FF9900', '#0078D4', '#FF6B35']  # AWS orange, Azure blue, Databricks orange
        bars = ax.bar(vendors, values, color=colors)

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f'{val:.2f}', ha='center', va='bottom')

        ax.set_title(f'{metric.replace("_", " ")}')
        ax.set_ylabel('Value')
        ax.grid(True, alpha=0.3)

    axes[-1].set_visible(False)
    plt.suptitle('Average Metrics by Vendor', fontsize=16)
    plt.tight_layout()
    plt.savefig('output/metrics_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Detailed Metrics by Dataset
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    for i, metric in enumerate(metrics):
        ax = axes[i]

        # Plot each vendor's datasets
        for v_idx, vendor in enumerate(vendors):
            datasets = results[vendor]['datasets']
            x_positions = []
            values = []

            for d_idx, (dataset, data) in enumerate(sorted(datasets.items())):
                x_pos = d_idx * (len(vendors) + 1) + v_idx
                x_positions.append(x_pos)
                values.append(data[metric])

            color = ['#FF9900', '#0078D4', '#FF6B35'][v_idx]
            ax.bar(x_positions, values, label=vendor, color=color, alpha=0.8)

        ax.set_title(f'{metric.replace("_", " ")} by Dataset')
        ax.set_xlabel('Datasets')
        ax.set_ylabel('Value')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Set x-ticks with meaningful dataset names
        tick_positions = [(i * (len(vendors) + 1) + len(vendors) / 2 - 0.5) for i in range(5)]
        ax.set_xticks(tick_positions)
        
        # Get the actual dataset names in the correct order
        sorted_datasets = sorted(results[vendors[0]]['datasets'].keys())
        dataset_labels = [dataset_names.get(dataset, dataset) for dataset in sorted_datasets]
        ax.set_xticklabels(dataset_labels, rotation=45)

    axes[-1].set_visible(False)
    plt.suptitle('All Metrics by Dataset and Vendor', fontsize=16)
    plt.tight_layout()
    plt.savefig('output/dataset_details.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 3. Metrics Summary Table
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('tight')
    ax.axis('off')

    # Create detailed table data
    headers = ['Vendor', 'Metric', 'Min', 'Max', 'Avg', 'Std Dev']
    table_data = [headers]

    for vendor in vendors:
        datasets = results[vendor]['datasets']

        for metric in metrics:
            values = [datasets[d][metric] for d in sorted(datasets.keys())]

            row = [
                vendor if metric == metrics[0] else '',  # Only show vendor name once
                metric.replace('_', ' '),
                f"{min(values):.3f}",
                f"{max(values):.3f}",
                f"{np.mean(values):.3f}",
                f"{np.std(values):.3f}"
            ]
            table_data.append(row)

        # Add separator row
        if vendor != vendors[-1]:
            table_data.append(['—'] * len(headers))

    table = ax.table(cellText=table_data, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)

    # Style header row
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#667eea')
        table[(0, i)].set_text_props(weight='bold', color='white')

    plt.title('Detailed Metrics Statistics', fontsize=16, pad=20)
    plt.savefig('output/metrics_table.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ Visualizations created")


if __name__ == "__main__":
    main()