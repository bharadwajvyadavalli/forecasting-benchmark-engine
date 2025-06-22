"""
Module for creating HTML dashboard dynamically based on available vendors and metrics
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def load_vendor_config():
    """Load vendor configuration from JSON file"""
    try:
        with open('vendor_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: vendor_config.json not found!")
        sys.exit(1)

def load_metrics_data():
    """Load metrics results"""
    try:
        with open('output/metrics_results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: metrics_results.json not found!")
        print("   Please run metrics_calculator.py first.")
        sys.exit(1)

def check_available_charts():
    """Check which visualization charts are available"""
    chart_files = [
        'metrics_comparison.png',
        'time_series_comparison.png',
        'error_distribution.png',
        'performance_heatmap.png',
        'accuracy_over_time.png'
    ]

    available_charts = []
    for chart in chart_files:
        if os.path.exists(f'output/{chart}'):
            available_charts.append(chart)

    return available_charts

def generate_vendor_cards(vendor_metrics, best_vendor):
    """Generate HTML for vendor metric cards"""
    cards_html = ""

    for vendor, metrics in sorted(vendor_metrics.items()):
        card_class = "vendor-card best-performer" if vendor == best_vendor else "vendor-card"
        badge = '<span class="best-badge">Best Performer</span>' if vendor == best_vendor else ''

        # Dynamically generate metric rows based on available metrics
        metric_rows = ""
        metric_order = ['MAE', 'MAPE', 'WAPE', 'RMSE', 'Bias', 'SMAPE', 'Tracking_Signal']

        for metric_name in metric_order:
            if metric_name in metrics:
                display_name = metric_name.replace('_', ' ')
                value = metrics[metric_name]

                # Format value based on metric type
                if metric_name in ['MAPE', 'WAPE', 'SMAPE']:
                    formatted_value = f"{value:.2f}%"
                elif metric_name == 'Tracking_Signal':
                    formatted_value = f"{value:.2f}"
                else:
                    formatted_value = f"${value:,.2f}"

                metric_rows += f"""
                    <div class="metric">
                        <span class="metric-name">{display_name}:</span>
                        <span class="metric-value">{formatted_value}</span>
                    </div>
                """

        cards_html += f"""
            <div class="{card_class}">
                <div class="vendor-name">{vendor}{badge}</div>
                {metric_rows}
            </div>
        """

    return cards_html

def generate_chart_sections(available_charts):
    """Generate HTML for available charts"""
    chart_info = {
        'metrics_comparison.png': {
            'title': '📊 Metrics Comparison',
            'description': 'Comparison of key accuracy metrics across all vendors'
        },
        'performance_heatmap.png': {
            'title': '🗺️ Performance Heatmap',
            'description': 'Normalized performance scores (higher is better)'
        },
        'time_series_comparison.png': {
            'title': '📈 Time Series Analysis',
            'description': 'Actual vs Forecast values over the analysis period'
        },
        'error_distribution.png': {
            'title': '📊 Error Distribution Analysis',
            'description': 'Distribution of forecast errors across all vendors'
        },
        'accuracy_over_time.png': {
            'title': '📈 Accuracy Trend Analysis',
            'description': 'Rolling forecast accuracy over time'
        }
    }

    # Group charts for better layout
    primary_charts = ['metrics_comparison.png', 'performance_heatmap.png']
    secondary_charts = ['time_series_comparison.png', 'error_distribution.png', 'accuracy_over_time.png']

    charts_html = ""

    # Primary charts in grid
    primary_available = [c for c in primary_charts if c in available_charts]
    if primary_available:
        charts_html += '<div class="charts-grid">\n'
        for chart in primary_available:
            info = chart_info.get(chart, {})
            charts_html += f"""
            <div class="chart-section">
                <h3 class="chart-title">{info.get('title', 'Chart')}</h3>
                <p class="chart-description">{info.get('description', '')}</p>
                <div class="chart-container">
                    <img src="{chart}" alt="{info.get('title', 'Chart')}">
                </div>
            </div>
            """
        charts_html += '</div>\n'

    # Secondary charts full width
    for chart in secondary_charts:
        if chart in available_charts:
            info = chart_info.get(chart, {})
            charts_html += f"""
        <div class="chart-section">
            <h3 class="chart-title">{info.get('title', 'Chart')}</h3>
            <p class="chart-description">{info.get('description', '')}</p>
            <div class="chart-container">
                <img src="{chart}" alt="{info.get('title', 'Chart')}">
            </div>
        </div>
        """

    return charts_html

def generate_html_dashboard(vendor_config, metrics_data, available_charts):
    """Generate the complete HTML dashboard"""
    vendor_metrics = metrics_data.get('metrics', {})
    metadata = metrics_data.get('metadata', {})
    best_vendor = metadata.get('best_performer_mape', '')

    # Count vendors
    n_vendors = len(vendor_metrics)

    # Generate dynamic content
    vendor_cards_html = generate_vendor_cards(vendor_metrics, best_vendor)
    charts_html = generate_chart_sections(available_charts)

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Forecasting Benchmark Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f0f2f5;
            color: #1a1a1a;
            line-height: 1.6;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 3rem 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .summary {{
            background: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 4px solid #667eea;
        }}
        
        .summary h2 {{
            color: #333;
            margin-bottom: 1rem;
            font-size: 1.8rem;
        }}
        
        .stats-row {{
            display: flex;
            gap: 2rem;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            flex: 1;
            min-width: 150px;
            text-align: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            color: #666;
            margin-top: 0.25rem;
        }}
        
        .metrics-section {{
            margin-bottom: 3rem;
        }}
        
        .section-title {{
            text-align: center;
            margin-bottom: 2rem;
            color: #333;
            font-size: 2rem;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }}
        
        .vendor-card {{
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .vendor-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }}
        
        .vendor-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        }}
        
        .vendor-card.best-performer {{
            background: linear-gradient(to bottom, #f0fff4 0%, #ffffff 100%);
        }}
        
        .vendor-card.best-performer::before {{
            background: linear-gradient(90deg, #48bb78 0%, #38a169 100%);
        }}
        
        .vendor-name {{
            font-size: 1.8rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 1.5rem;
            text-align: center;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-name {{
            font-weight: 600;
            color: #4a5568;
        }}
        
        .metric-value {{
            font-weight: bold;
            color: #2d3748;
        }}
        
        .best-badge {{
            display: inline-block;
            background: #48bb78;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-left: 1rem;
        }}
        
        .chart-section {{
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
        }}
        
        .chart-title {{
            font-size: 1.5rem;
            color: #333;
            margin-bottom: 0.5rem;
            text-align: center;
        }}
        
        .chart-description {{
            text-align: center;
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }}
        
        .chart-container {{
            text-align: center;
            overflow-x: auto;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .footer {{
            text-align: center;
            padding: 3rem 2rem;
            color: #718096;
            border-top: 1px solid #e2e8f0;
            margin-top: 4rem;
        }}
        
        .footer p {{
            margin: 0.5rem 0;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 2rem;
        }}
        
        .no-data {{
            text-align: center;
            padding: 3rem;
            color: #666;
            font-style: italic;
        }}
        
        @media (max-width: 768px) {{
            header h1 {{
                font-size: 2rem;
            }}
            
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .container {{
                padding: 1rem;
            }}
            
            .stats-row {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Forecasting Benchmark Dashboard</h1>
        <p>Comprehensive forecast accuracy analysis across {n_vendors} vendor{'s' if n_vendors != 1 else ''}</p>
        <p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">24-Month Analysis Period</p>
    </header>
    
    <div class="container">
        <div class="summary">
            <h2>📊 Executive Summary</h2>
            <p>This dashboard presents a comprehensive analysis of forecasting accuracy for cloud service providers. The analysis evaluates multiple accuracy metrics to provide insights into forecast performance and reliability.</p>
            
            <div class="stats-row">
                <div class="stat-item">
                    <div class="stat-value">{n_vendors}</div>
                    <div class="stat-label">Vendors Analyzed</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(available_charts)}</div>
                    <div class="stat-label">Visualizations</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(next(iter(vendor_metrics.values()))) if vendor_metrics else 0}</div>
                    <div class="stat-label">Metrics Per Vendor</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{best_vendor or 'N/A'}</div>
                    <div class="stat-label">Best Performer</div>
                </div>
            </div>
        </div>
        
        <div class="metrics-section">
            <h2 class="section-title">📈 Vendor Performance Metrics</h2>
            
            <div class="metrics-grid">
                {vendor_cards_html}
            </div>
        </div>
        
        {charts_html if charts_html else '<div class="no-data">No visualization charts available. Please run visualization_generator.py to create charts.</div>'}
    </div>
    
    <footer class="footer">
        <p><strong>Generated on:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Data Source:</strong> vendor_config.json ({n_vendors} vendors)</p>
        <p><strong>Forecasting Benchmark Engine</strong> - Dynamic Analysis Tool</p>
    </footer>
</body>
</html>
"""

    return html_content

def main():
    """Main function to create HTML dashboard"""
    print("🎨 Dashboard Creator Module")
    print("=" * 50)

    # Check if output directory exists
    os.makedirs('output', exist_ok=True)

    # Load vendor configuration
    print("\n📊 Loading vendor configuration...")
    vendor_config = load_vendor_config()

    # Load metrics data
    print("📊 Loading metrics data...")
    metrics_data = load_metrics_data()

    vendor_metrics = metrics_data.get('metrics', {})
    if not vendor_metrics:
        print("❌ Error: No vendor metrics found!")
        sys.exit(1)

    print(f"   ✅ Found metrics for {len(vendor_metrics)} vendor(s)")

    # Check available charts
    print("\n🎨 Checking available visualizations...")
    available_charts = check_available_charts()

    if available_charts:
        print(f"   ✅ Found {len(available_charts)} visualization(s):")
        for chart in available_charts:
            print(f"      - {chart}")
    else:
        print("   ⚠️  No visualizations found. Dashboard will show metrics only.")
        print("      Run visualization_generator.py to create charts.")

    # Generate HTML dashboard
    print("\n📄 Generating HTML dashboard...")
    html_content = generate_html_dashboard(vendor_config, metrics_data, available_charts)

    # Save dashboard
    with open('output/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("\n✅ Dashboard creation completed!")
    print("📁 Dashboard saved to output/dashboard.html")
    print("\n🌐 Open output/dashboard.html in your browser to view the dashboard")

    # Display summary
    metadata = metrics_data.get('metadata', {})
    if metadata.get('best_performer_mape'):
        print(f"\n🏆 Best Performer: {metadata['best_performer_mape']}")

if __name__ == "__main__":
    main()