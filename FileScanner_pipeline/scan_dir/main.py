import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from create_samplesheet import *
from launch_basecalling_run import launch_run
from Basecalling_pipeline.monitor_run.bot_telegram import telegram_send_bar
from Basecalling_pipeline.monitor_run.bot_telegram import telegram_send_file

# ANSI escape code for green text
GREEN = "\033[92m"
RESET = "\033[0m"
RED = "\033[91m"


if __name__ == "__main__":
    dir = sys.argv[1]
    model = sys.argv[2]
    outputLocation = sys.argv[3]
    #TODO is correct here. If it already exist nothing happen, otherwise we are ok
    os.makedirs(outputLocation, exist_ok=True)
    
    samplesheet_not_found = False
    added_files = 0

    #Look for existing samplesheet
    existing_samplesheet = list_json(dir)
    if len(existing_samplesheet) == 0:
        print(f"I wasn't able to find any existing samplesheet inside {GREEN}{dir}{RESET}")
        #Create a new samplesheet
        samplesheet = Samplesheet(create_blank_samplesheet(dir, model, outputLocation))
        print("A {GREEN}new samplesheet was created{RESET}")
        added_files = update_samplesheet(samplesheet)
    else: 
        for sheet in existing_samplesheet:
            if is_same_samplesheet(sheet, dir, model, outputLocation):
                print(f"An EXISTING samplesheet for {GREEN}{model}{GREEN} was found inside {GREEN}{dir}{RESET}")
                samplesheet = Samplesheet(sheet)
                added_files = update_samplesheet(samplesheet)
                samplesheet_not_found = False
                break
            else:
                samplesheet_not_found = True

    if samplesheet_not_found :    
        #Create a new samplesheet
        samplesheet = Samplesheet(create_blank_samplesheet(dir, model, outputLocation))
        print(f"A {GREEN}new samplesheet{RESET} was created")
        added_files = update_samplesheet(samplesheet)

    # Get the current date and time
    current_datetime = datetime.now()
    # Format the datetime to [DD/Mon/YYYY HH:MM:SS]
    formatted_datetime = current_datetime.strftime("%d/%b/%Y %H:%M:%S")   
    message = f"Scan of {dir} at {formatted_datetime} added {added_files} files to {samplesheet.file_path}"
    telegram_send_bar(message)
    
    if added_files>0:
        launch_run(samplesheet)