"""
Create HTML dashboard for benchmark results
"""
import json
import os
from datetime import datetime


def load_results():
    """Load benchmark results"""
    with open('output/benchmark_results.json', 'r') as f:
        return json.load(f)


def generate_dashboard():
    """Generate HTML dashboard"""
    results = load_results()

    # Generate vendor cards HTML
    vendor_cards = ""
    for vendor_name, vendor_data in results['vendors'].items():
        # Calculate average MAPE
        mapes = []
        for dataset_data in vendor_data.values():
            if 'metrics' in dataset_data:
                mapes.append(dataset_data['metrics']['MAPE'])
        avg_mape = sum(mapes) / len(mapes) if mapes else 0

        # Check if best overall
        is_best = False
        if 'overall_best' in results['summary']:
            is_best = results['summary']['overall_best']['vendor'] == vendor_name

        vendor_cards += f"""
        <div class="vendor-card {'best-vendor' if is_best else ''}">
            <h3>{vendor_name} {'👑' if is_best else ''}</h3>
            <div class="metric-value">{avg_mape:.1f}%</div>
            <div class="metric-label">Average MAPE</div>
        </div>
        """

    # Generate dataset results table
    table_rows = ""
    datasets = list(results['summary'].keys())
    if 'overall_best' in datasets:
        datasets.remove('overall_best')

    for dataset in datasets:
        row = f"<tr><td>{dataset}</td>"
        for vendor in results['vendors']:
            if dataset in results['vendors'][vendor] and 'metrics' in results['vendors'][vendor][dataset]:
                mape = results['vendors'][vendor][dataset]['metrics']['MAPE']
                is_best = results['summary'][dataset]['best_vendor'] == vendor
                row += f'<td class="{"best-cell" if is_best else ""}">{mape:.1f}%</td>'
            else:
                row += '<td>-</td>'
        row += "</tr>"
        table_rows += row

    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Forecast Benchmarking Results</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
        }}
        .vendor-cards {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 40px;
        }}
        .vendor-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            min-width: 150px;
        }}
        .vendor-card.best-vendor {{
            background: #e7f5e7;
            border: 2px solid #4CAF50;
        }}
        .vendor-card h3 {{
            margin: 0 0 15px 0;
            color: #333;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #2196F3;
        }}
        .metric-label {{
            color: #666;
            font-size: 14px;
        }}
        .results-table {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 0 auto 40px;
            max-width: 800px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f8f8;
            font-weight: bold;
        }}
        .best-cell {{
            background-color: #e7f5e7;
            font-weight: bold;
        }}
        .charts {{
            text-align: center;
            margin-top: 40px;
        }}
        .charts img {{
            max-width: 100%;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Forecast Benchmarking Dashboard</h1>
        <div class="timestamp">Generated: {results['timestamp']}</div>
    </div>

    <div class="vendor-cards">
        {vendor_cards}
    </div>

    <div class="results-table">
        <table>
            <thead>
                <tr>
                    <th>Dataset</th>
                    <th>AWS</th>
                    <th>Azure</th>
                    <th>Databricks</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>

    <div class="charts">
        <h2>Performance Visualizations</h2>
        <img src="vendor_heatmap.png" alt="Vendor Performance Heatmap">
        <img src="summary_chart.png" alt="Summary Chart">
        <img src="metrics_comparison.png" alt="Metrics Comparison">
    </div>
</body>
</html>
"""

    with open('output/dashboard.html', 'w') as f:
        f.write(html)

    print("✓ Dashboard saved to output/dashboard.html")


def main():
    generate_dashboard()


if __name__ == "__main__":
    main()