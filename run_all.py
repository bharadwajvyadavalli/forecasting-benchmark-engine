import subprocess
import sys
import os

def run(script):
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if result.stdout: print(result.stdout)
    if result.returncode != 0:
        if result.stderr: print(result.stderr)
        return False
    return True

def main():
    print("Forecasting Benchmark Pipeline\n")

    # Create default config if missing
    if not os.path.exists('vendor_config.json'):
        with open('vendor_config.json', 'w') as f:
            f.write('''{
  "vendors": [
    {"name": "AWS", "forecast_files": {"dataset1": "input/aws_dataset1_forecast.csv", "dataset2": "input/aws_dataset2_forecast.csv", "dataset3": "input/aws_dataset3_forecast.csv", "dataset4": "input/aws_dataset4_forecast.csv", "dataset5": "input/aws_dataset5_forecast.csv"}},
    {"name": "Azure", "forecast_files": {"dataset1": "input/azure_dataset1_forecast.csv", "dataset2": "input/azure_dataset2_forecast.csv", "dataset3": "input/azure_dataset3_forecast.csv", "dataset4": "input/azure_dataset4_forecast.csv", "dataset5": "input/azure_dataset5_forecast.csv"}},
    {"name": "Databricks", "forecast_files": {"dataset1": "input/databricks_dataset1_forecast.csv", "dataset2": "input/databricks_dataset2_forecast.csv", "dataset3": "input/databricks_dataset3_forecast.csv", "dataset4": "input/databricks_dataset4_forecast.csv", "dataset5": "input/databricks_dataset5_forecast.csv"}}
  ]
}''')

    scripts = ["forecast_generator.py", "metrics_calculator.py", "visualization_generator.py", "dashboard_creator.py"]

    for script in scripts:
        print(f"\nRunning {script}...")
        if not run(script):
            print(f"Failed at {script}")
            break
    else:
        print("\n✅ Done! Open output/dashboard.html")

if __name__ == "__main__":
    main()