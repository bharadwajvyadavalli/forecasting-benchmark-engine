import pandas as pd
import numpy as np
import json
import os
from scipy import stats
from sklearn.metrics import f1_score

def calculate_metrics(actual, forecast):
    residuals = actual - forecast

    # Bias
    bias = np.mean(forecast - actual)

    # CRPS (simplified)
    crps = np.mean(np.abs(residuals)) + 0.5 * np.std(residuals)

    # Residual Anomaly %
    anomaly_pct = (np.abs(stats.zscore(residuals)) > 3).sum() / len(residuals) * 100

    # Data Drift
    mid = len(actual) // 2
    if mid > 0:
        drift = abs(np.mean(actual[:mid]) - np.mean(actual[mid:])) / (np.std(actual) + 1e-10)
    else:
        drift = 0.0

    # Turning Point F1
    try:
        actual_turns = np.diff(np.sign(np.diff(actual))) != 0
        forecast_turns = np.diff(np.sign(np.diff(forecast))) != 0
        tp_f1 = f1_score(actual_turns[:min(len(actual_turns), len(forecast_turns))],
                        forecast_turns[:min(len(actual_turns), len(forecast_turns))])
    except:
        tp_f1 = 0.0

    return {
        'Bias': round(bias, 2),
        'CRPS': round(crps, 2),
        'Residual_Anomaly_%': round(anomaly_pct, 2),
        'Data_Drift': round(drift, 4),
        'Turning_Point_F1': round(tp_f1, 4)
    }

def main():
    with open('vendor_config.json') as f:
        config = json.load(f)

    results = {}

    for vendor in config['vendors']:
        name = vendor['name']
        files = vendor.get('forecast_files', {'single': vendor.get('forecast_file')})

        vendor_metrics = {}
        for dataset, path in files.items():
            try:
                df = pd.read_csv(path)
                if 'Actual' in df and 'Forecast' in df:
                    vendor_metrics[dataset] = calculate_metrics(df['Actual'].values, df['Forecast'].values)
            except:
                pass

        if vendor_metrics:
            # Average metrics
            avg = {}
            for metric in ['Bias', 'CRPS', 'Residual_Anomaly_%', 'Data_Drift', 'Turning_Point_F1']:
                avg[metric] = round(np.mean([m[metric] for m in vendor_metrics.values()]), 4)

            results[name] = {
                'average': avg,
                'datasets': vendor_metrics,
                'dataset_count': len(vendor_metrics)
            }

    os.makedirs('output', exist_ok=True)
    with open('output/metrics_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n📊 Results:")
    print(f"{'Vendor':<15} {'Bias':<8} {'CRPS':<8} {'Anomaly%':<10} {'Drift':<8} {'TP-F1':<8}")
    print("-" * 60)

    for vendor, data in results.items():
        avg = data['average']
        print(f"{vendor:<15} {avg['Bias']:<8.2f} {avg['CRPS']:<8.2f} "
              f"{avg['Residual_Anomaly_%']:<10.2f} {avg['Data_Drift']:<8.4f} "
              f"{avg['Turning_Point_F1']:<8.4f}")

if __name__ == "__main__":
    main()