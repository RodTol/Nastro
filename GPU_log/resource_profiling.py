import psutil
import time
import csv
from datetime import datetime
import argparse

def profile_resources(slurm_mem, slurm_cpu_number, csv_path, tag):
    max_cpu = 0.0
    max_mem = 0.0

    try:
        while True:
            # Measure current usage
            cpu_usage = psutil.cpu_percent(interval=1)
            mem_usage = psutil.virtual_memory().percent

            # Update max values if current values are higher
            max_cpu = max(max_cpu, cpu_usage)
            max_mem = max(max_mem, mem_usage)
            time.sleep(2)

    except KeyboardInterrupt:
        # Save the data upon job completion
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = csv_path if csv_path else "resource_usage.csv"
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Max CPU Usage (%)", "Max Memory Usage (%)", "SLURM Memory", "SLURM CPU Number", "Tag"])
            writer.writerow([timestamp, max_cpu, max_mem, float(slurm_mem), float(slurm_cpu_number), tag])
        print(f"Resource usage data saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Profile resource usage.")
    parser.add_argument("slurm_mem", type=str, help="SLURM memory allocation")
    parser.add_argument("slurm_cpu_number", type=str, help="SLURM CPU number allocation")
    parser.add_argument("csv_path", type=str, help="Path to save the CSV file")
    parser.add_argument("tag", type=str, help="Tag for the job")

    args = parser.parse_args()

    profile_resources(
        slurm_mem=args.slurm_mem,
        slurm_cpu_number=args.slurm_cpu_number,
        csv_path=args.csv_path,
        tag=args.tag
    )

if __name__ == "__main__":
    main()
