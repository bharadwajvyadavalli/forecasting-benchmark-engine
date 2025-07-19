import json
from datetime import datetime


def main():
    with open('output/metrics_results.json') as f:
        results = json.load(f)

    # Find best performers
    best = {
        'bias': min(results, key=lambda v: abs(results[v]['average']['Bias'])),
        'crps': min(results, key=lambda v: results[v]['average']['CRPS']),
        'tp': max(results, key=lambda v: results[v]['average']['Turning_Point_F1'])
    }

    # Generate vendor cards
    cards = ""
    for vendor, data in results.items():
        avg = data['average']
        badges = []

        if vendor == best['bias']: badges.append('<span class="badge">Best Bias</span>')
        if vendor == best['crps']: badges.append('<span class="badge">Best CRPS</span>')
        if vendor == best['tp']: badges.append('<span class="badge">Best TP</span>')

        cards += f"""
        <div class="card">
            <h3>{vendor} {''.join(badges)}</h3>
            <p>{data['dataset_count']} datasets analyzed</p>
            <table>
                <tr><td>Bias:</td><td>{avg['Bias']:.2f}</td></tr>
                <tr><td>CRPS:</td><td>{avg['CRPS']:.2f}</td></tr>
                <tr><td>Anomaly %:</td><td>{avg['Residual_Anomaly_%']:.2f}%</td></tr>
                <tr><td>Data Drift:</td><td>{avg['Data_Drift']:.4f}</td></tr>
                <tr><td>TP F1:</td><td>{avg['Turning_Point_F1']:.4f}</td></tr>
            </table>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Forecast Benchmark</title>
    <style>
        body {{ font-family: Arial; margin: 0; background: #f5f5f5; }}
        header {{ background: #667eea; color: white; padding: 2rem; text-align: center; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }}
        .card {{ background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h3 {{ margin: 0 0 1rem 0; }}
        .badge {{ background: #48bb78; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-left: 0.5rem; }}
        table {{ width: 100%; }}
        td {{ padding: 0.5rem 0; }}
        td:first-child {{ color: #666; }}
        td:last-child {{ font-weight: bold; text-align: right; }}
        .charts {{ background: white; padding: 2rem; border-radius: 8px; margin-top: 2rem; }}
        img {{ max-width: 100%; margin: 1rem 0; }}
    </style>
</head>
<body>
    <header>
        <h1>Forecasting Benchmark Dashboard</h1>
        <p>Advanced metrics across {len(results)} vendors</p>
    </header>

    <div class="container">
        <div class="cards">
            {cards}
        </div>

        <div class="charts">
            <h2>Visualizations</h2>
            <img src="metrics_comparison.png" alt="Metrics">
            <img src="dataset_details.png" alt="Dataset Details">
            <img src="metrics_table.png" alt="Metrics Summary">
        </div>
    </div>
</body>
</html>"""

    with open('output/dashboard.html', 'w') as f:
        f.write(html)

    print("✅ Dashboard created")


if __name__ == "__main__":
    main()