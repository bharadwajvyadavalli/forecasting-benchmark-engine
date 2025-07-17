import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np


def main():
    with open('output/metrics_results.json') as f:
        results = json.load(f)

    vendors = list(results.keys())
    metrics = ['Bias', 'CRPS', 'Residual_Anomaly_%', 'Data_Drift', 'Turning_Point_F1']

    # 1. Metrics Comparison
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()

    for i, metric in enumerate(metrics):
        ax = axes[i]
        values = [results[v]['average'][metric] for v in vendors]
        bars = ax.bar(vendors, values, color=sns.color_palette('viridis', len(vendors)))

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f'{val:.2f}', ha='center', va='bottom')

        ax.set_title(metric.replace('_', ' '))
        ax.grid(True, alpha=0.3)

    axes[-1].set_visible(False)
    plt.suptitle('Average Metrics Across Datasets', fontsize=14)
    plt.tight_layout()
    plt.savefig('output/metrics_comparison.png', dpi=150)
    plt.close()

    # 2. Detailed Metrics by Dataset
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
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

            ax.bar(x_positions, values, label=vendor, alpha=0.8)

        ax.set_title(metric.replace('_', ' '))
        ax.set_xlabel('Datasets')
        ax.set_ylabel('Value')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Set x-ticks
        tick_positions = [(i * (len(vendors) + 1) + len(vendors) / 2 - 0.5) for i in range(5)]
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([f'D{i + 1}' for i in range(5)])

    axes[-1].set_visible(False)
    plt.suptitle('All Metrics by Dataset and Vendor', fontsize=14)
    plt.tight_layout()
    plt.savefig('output/dataset_details.png', dpi=150)
    plt.close()

    # 3. Metrics Summary Table
    fig, ax = plt.subplots(figsize=(12, 8))
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

    plt.title('Detailed Metrics Statistics Across All Datasets', fontsize=16, pad=20)
    plt.savefig('output/metrics_table.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 4. Heatmap of all metrics
    fig, ax = plt.subplots(figsize=(12, 10))

    # Prepare data for heatmap
    heatmap_data = []
    row_labels = []

    for vendor in vendors:
        for dataset in sorted(results[vendor]['datasets'].keys()):
            row_labels.append(f"{vendor}-{dataset}")
            row_data = [results[vendor]['datasets'][dataset][m] for m in metrics]
            heatmap_data.append(row_data)

    # Normalize each metric column (0-1)
    heatmap_array = np.array(heatmap_data)
    normalized_data = np.zeros_like(heatmap_array)

    for i, metric in enumerate(metrics):
        col = heatmap_array[:, i]
        if metric == 'Turning_Point_F1':  # Higher is better
            normalized_data[:, i] = (col - col.min()) / (col.max() - col.min() + 1e-10)
        else:  # Lower is better
            normalized_data[:, i] = 1 - (col - col.min()) / (col.max() - col.min() + 1e-10)

    im = ax.imshow(normalized_data, cmap='RdYlGn', aspect='auto')

    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels([m.replace('_', ' ') for m in metrics])
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels)

    # Add values on cells
    for i in range(len(row_labels)):
        for j in range(len(metrics)):
            text = ax.text(j, i, f'{heatmap_array[i, j]:.2f}',
                           ha='center', va='center', fontsize=8)

    plt.colorbar(im, ax=ax, label='Performance (Higher = Better)')
    plt.title('All Metrics Heatmap (Values shown, Colors normalized)', fontsize=14)
    plt.tight_layout()
    plt.savefig('output/metrics_heatmap.png', dpi=150)
    plt.close()

    print("✅ Visualizations created")


if __name__ == "__main__":
    main()