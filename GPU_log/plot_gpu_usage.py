import pandas as pd
import matplotlib.pyplot as plt
import sys

def plot_gpu_usage(log_file, output_image):
    # Load the log data
    df = pd.read_csv(log_file)

    # Convert timestamp column to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Create a plot for each GPU
    plt.figure(figsize=(10, 5))
    for gpu_id in df['gpu_id'].unique():
        gpu_data = df[df['gpu_id'] == gpu_id]
        plt.plot(gpu_data['timestamp'], gpu_data['gpu_usage'], label=f'GPU {gpu_id}')

    # Customize plot
    plt.xlabel('Time')
    plt.ylabel('GPU Usage (%)')
    plt.title('GPU Usage Over Time')
    plt.legend()

    # Save the plot to an image file
    plt.savefig(output_image)
    print(f"Plot saved to {output_image}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python plot_gpu_usage.py /path/to/logfile.csv /path/to/output_image.png")
        sys.exit(1)
    
    log_file = sys.argv[1]
    output_image = sys.argv[2]
    plot_gpu_usage(log_file, output_image)
