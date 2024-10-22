import os
import time
import csv
import subprocess
import sys

def log_gpu_usage(log_file, interval=2):
    # Create the log file and write the header if it doesn't exist
    file_exists = os.path.isfile(log_file)
    with open(log_file, 'a') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'gpu_id', 'gpu_usage', 'memory_usage'])

        while True:
            # Run nvidia-smi to get the GPU stats
            result = subprocess.run(['nvidia-smi', '--query-gpu=index,utilization.gpu,utilization.memory', '--format=csv,noheader,nounits'],
                                    stdout=subprocess.PIPE, text=True)
            
            # Get current timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            # Parse the output and log it
            for line in result.stdout.strip().split('\n'):
                gpu_data = [timestamp] + line.split(',')
                writer.writerow([item.strip() for item in gpu_data])

            f.flush()
            time.sleep(interval)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python collect_gpu_data.py /path/to/logfile.csv")
        sys.exit(1)
    
    log_file = sys.argv[1]
    log_gpu_usage(log_file)
