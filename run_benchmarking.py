"""
Main script to run the complete benchmarking pipeline
"""
import os
import subprocess
import sys

def run_step(script_name, description):
    """Run a step in the pipeline"""
    print(f"\n{description}...")
    try:
        subprocess.run([sys.executable, script_name], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Error running {script_name}")
        return False
    except FileNotFoundError:
        print(f"✗ {script_name} not found")
        return False

def main():
    print("=" * 60)
    print("FORECAST BENCHMARKING ENGINE")
    print("=" * 60)

    # Check if we need to generate sample data
    if not os.path.exists('input'):
        print("\nNo input folder found. Generating sample data...")
        if not run_step('generate_sample_data.py', 'Generating sample forecast data'):
            return

    # Run benchmarking
    if not run_step('benchmark_engine.py', 'Running benchmark analysis'):
        return

    # Create visualizations
    if not run_step('create_visualizations.py', 'Creating visualizations'):
        return

    # Create dashboard
    if not run_step('create_dashboard.py', 'Creating dashboard'):
        return

    print("\n" + "=" * 60)
    print("✓ BENCHMARKING COMPLETE!")
    print("=" * 60)
    print("\nResults available in output/")
    print("Open output/dashboard.html to view the dashboard")

if __name__ == "__main__":
    main()