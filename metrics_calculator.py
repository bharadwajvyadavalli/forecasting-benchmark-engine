import numpy as np
import pandas as pd
import json
import os
from scipy import stats
from scipy.stats import ks_2samp
from sklearn.metrics import f1_score
from statsmodels import robust

def generate_forecast_samples(actual, forecast, n_samples=1000):
    residuals = actual - forecast
    mad = robust.mad(residuals)
    std_estimate = mad * 1.4826  # MAD to std approximation
    forecast_samples = np.random.normal(loc=forecast[:, None], scale=std_estimate, size=(len(forecast), n_samples))
    return forecast_samples

def crps_manual(y, forecast_samples):
    forecast_samples = np.sort(forecast_samples)
    n = len(forecast_samples)
    empirical_cdf = np.searchsorted(forecast_samples, y, side='right') / n
    crps = np.mean((forecast_samples - y) ** 2) - np.mean((forecast_samples[:, None] - forecast_samples) ** 2) / 2
    return crps

def calculate_crps_all(actual, forecast_samples):
    crps_values = [crps_manual(y, fs) for y, fs in zip(actual, forecast_samples)]
    return np.mean(crps_values)

def calculate_metrics(actual, forecast, n_samples=1000):
    actual = np.array(actual)
    forecast = np.array(forecast)

    residuals = actual - forecast

    # Bias
    bias = np.mean(forecast - actual)

    # Forecast Samples
    forecast_samples = generate_forecast_samples(actual, forecast, n_samples)

    # Bias-Adjusted Spread CRPS
    forecast_centered = forecast - bias
    forecast_samples_centered = forecast_samples - bias
    spread_crps = calculate_crps_all(actual, forecast_samples_centered)

    # Residual Anomaly % (Z-score)
    z_scores = stats.zscore(residuals)
    anomaly_pct = (np.abs(z_scores) > 3).sum() / len(residuals) * 100

    # Data Drift (KS Test)
    mid = len(actual) // 2
    drift = ks_2samp(actual[:mid], actual[mid:])[0] if mid > 0 else 0.0

    # Turning Point F1 Score
    try:
        actual_turns = (np.diff(np.sign(np.diff(actual))) != 0).astype(int)
        forecast_turns = (np.diff(np.sign(np.diff(forecast))) != 0).astype(int)
        min_len = min(len(actual_turns), len(forecast_turns))
        tp_f1 = f1_score(actual_turns[:min_len], forecast_turns[:min_len])
    except:
        tp_f1 = 0.0

    return {
        'Bias': round(bias, 2),
        'CRPS': round(spread_crps, 4),
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
        files = vendor.get('forecast_files', {})

        vendor_metrics = {}
        for dataset, path in files.items():
            try:
                df = pd.read_csv(path)
                if 'Actual' in df and 'Forecast' in df:
                    vendor_metrics[dataset] = calculate_metrics(df['Actual'].values, df['Forecast'].values)
            except Exception as e:
                print(f"Error processing {dataset} for {name}: {e}")
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