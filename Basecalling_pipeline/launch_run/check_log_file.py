import time
import argparse

def monitor_log(log_path, target_line="Press CTRL+C to quit"):
    """
    Monitors the log file at log_path and returns True when target_line is found.
    
    :param log_path: Path to the log file.
    :param target_line: The line to search for in the log file.
    :return: True if target_line is found, otherwise False.
    """
    try:
        with open(log_path, 'r') as file:
            while True:
                line = file.readline()
                if not line:
                    time.sleep(1)  # Wait for new lines to be written
                    continue
                if target_line in line:
                    return True
    except FileNotFoundError:
        print(f"The file {log_path} does not exist.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor a log file for a specific line.")
    parser.add_argument('log_path', type=str, help="The path to the log file.")
    parser.add_argument('target_line', type=str, help="The target line to search for in the log file.")
    
    args = parser.parse_args()
    
    found = monitor_log(args.log_path, args.target_line)
    if found:
        print("Target line found in the log file.")
    else:
        print("Target line not found in the log file.")
