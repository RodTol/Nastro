import os
import sys
import shutil
import time


def list_all_pod5_files(input_dir) :
    all_files= os.listdir(input_dir)
    pod5_files = [file for file in all_files if file.endswith('.pod5')]
    return pod5_files

def mimic_live_writing(src_dir, dest_dir, interval_seconds=10):
    files = list_all_pod5_files(src_dir)
    files_set = set(files)  # Set to keep track of copied files

    for file in files_set:    
        src_file_path = os.path.join(src_dir, file)
        dest_file_path = os.path.join(dest_dir, file)

        print(f"Copying file: {file}", end=" ")
        shutil.copy(src_file_path, dest_file_path)
        print("Copy successful", flush=True)

        time.sleep(interval_seconds)
        

def mimic_live_writing_groups(src_dir, dest_dir, interval_seconds=10, n_files=4):
    files = list_all_pod5_files(src_dir)
    files_set = set(files)  # Set to keep track of copied files
    
    counter = 0

    for file in files_set:   
        counter = counter+1 
        src_file_path = os.path.join(src_dir, file)
        dest_file_path = os.path.join(dest_dir, file)

        print(f"Copying file: {file}", end=" ")
        shutil.copy(src_file_path, dest_file_path)
        print("Copy successful", flush=True)

        if (counter==n_files):
            print("PAUSE")
            counter=0
            time.sleep(interval_seconds)
    
    print("No new files to copy.")

if __name__ == "__main__":
    src_dir = sys.argv[1]  # Source directory
    dest_dir = sys.argv[2]    # Destination directory

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    mimic_live_writing(src_dir, dest_dir)
    #mimic_live_writing_groups(src_dir, dest_dir)
