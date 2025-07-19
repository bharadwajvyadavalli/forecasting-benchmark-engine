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
  "datasets": [
    "monthly_car_sales",
    "us_auto_inventory", 
    "sunspots",
    "shampoo_sales",
    "air_passengers"
  ],
  "vendors": [
    {"name": "AWS", "forecast_files": {"monthly_car_sales": "input/aws_monthly_car_sales_forecast.csv", "us_auto_inventory": "input/aws_us_auto_inventory_forecast.csv", "sunspots": "input/aws_sunspots_forecast.csv", "shampoo_sales": "input/aws_shampoo_sales_forecast.csv", "air_passengers": "input/aws_air_passengers_forecast.csv"}},
    {"name": "Azure", "forecast_files": {"monthly_car_sales": "input/azure_monthly_car_sales_forecast.csv", "us_auto_inventory": "input/azure_us_auto_inventory_forecast.csv", "sunspots": "input/azure_sunspots_forecast.csv", "shampoo_sales": "input/azure_shampoo_sales_forecast.csv", "air_passengers": "input/azure_air_passengers_forecast.csv"}},
    {"name": "Databricks", "forecast_files": {"monthly_car_sales": "input/databricks_monthly_car_sales_forecast.csv", "us_auto_inventory": "input/databricks_us_auto_inventory_forecast.csv", "sunspots": "input/databricks_sunspots_forecast.csv", "shampoo_sales": "input/databricks_shampoo_sales_forecast.csv", "air_passengers": "input/databricks_air_passengers_forecast.csv"}}
  ]
}''')

    scripts = ["data_generator.py", "forecast_generator.py", "metrics_calculator.py", "visualization_generator.py", "dashboard_creator.py"]

    for script in scripts:
        print(f"\nRunning {script}...")
        if not run(script):
            print(f"Failed at {script}")
            break
    else:
        print("\n✅ Done! Open output/dashboard.html")

if __name__ == "__main__":
    main()