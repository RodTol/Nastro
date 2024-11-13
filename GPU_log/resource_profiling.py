import psutil
import time
import csv
from datetime import datetime
import sys

def profile_resources(slurm_mem, slurm_cpu_number, csv_path, tag):
    max_cpu = 0.0
    max_mem = 0.0

    try:
        while True:
            # Measure current usage
            cpu_usage = psutil.cpu_percent(interval=1)
            mem_usage = psutil.virtual_memory().used / (1024 ** 3)  # Convert bytes to GB

            # Update max values if current values are higher
            max_cpu = max(max_cpu, cpu_usage)
            max_mem = max(max_mem, mem_usage)
            time.sleep(2)

            slurm_mem_gb = float(slurm_mem) / 1024

    except KeyboardInterrupt:
        # Save the data upon job completion
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = csv_path if csv_path else "resource_usage.csv"
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Max CPU Usage (%)", "Max Memory Usage (%)", "SLURM Memory", "SLURM CPU Number", "Tag"])
            writer.writerow([timestamp, max_cpu, max_mem, float(slurm_mem_gb), float(slurm_cpu_number), tag])
        print(f"Resource usage data saved to {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python3 resource_profiling.py <SLURM_MEM> <SLURM_CPU_NUMBER> <CSV_PATH> <TAG>")
        sys.exit(1)

    slurm_mem = sys.argv[1]
    slurm_cpu_number = sys.argv[2]
    csv_path = sys.argv[3]
    tag = sys.argv[4]

    profile_resources(slurm_mem, slurm_cpu_number, csv_path, tag)
