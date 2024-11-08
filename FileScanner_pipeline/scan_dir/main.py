#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"

import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from create_samplesheet import *
from launch_basecalling_run import launch_run
from Basecalling_pipeline.monitor_run.bot_telegram import telegram_send_bar
from Basecalling_pipeline.monitor_run.bot_telegram import Telegram_bar
from Basecalling_pipeline.monitor_run.progress_bar import *

# ANSI escape code for green text
GREEN = "\033[92m"
RESET = "\033[0m"
RED = "\033[91m"


if __name__ == "__main__":
    dir = sys.argv[1]
    model = sys.argv[2]
    outputLocation = sys.argv[3]
    os.makedirs(outputLocation, exist_ok=True)

    message = f"""-----SCAN-RUN-----
I am going to scan `{dir}`
    """
    telegram_send_bar(message)

    samplesheet_not_found = False
    added_files = 0

    all_pod5_files_in_dir = list_pod5(dir)
    bar = CustomPercentProgressBar(length=20,
                            left_limit='[',
                            right_limit=']',
                            head_repr='>',
                            empty_repr=' ',
                            filled_repr='=',
                            start=0,
                            scale_start=0,
                            scale_end=len(all_pod5_files_in_dir))
    telegram_bar = Telegram_bar()

    #Look for existing samplesheet
    existing_samplesheet = list_json(dir)
    if len(existing_samplesheet) == 0:
        print(f"I wasn't able to find any existing samplesheet inside {GREEN}{dir}{RESET}", flush=True)
        #Create a new samplesheet
        samplesheet = Samplesheet(create_blank_samplesheet(dir, model, outputLocation))
        print(f"A {GREEN}new samplesheet was created{RESET}", flush=True)
        added_files = update_samplesheet(samplesheet, bar, telegram_bar)
    else: 
        for sheet in existing_samplesheet:
            if is_same_samplesheet(sheet, dir, model, outputLocation):
                print(f"An EXISTING samplesheet for {GREEN}{model}{GREEN} was found inside {GREEN}{dir}{RESET}", flush=True)
                samplesheet = Samplesheet(sheet)
                added_files = update_samplesheet(samplesheet, bar, telegram_bar)
                samplesheet_not_found = False
                break
            else:
                samplesheet_not_found = True

    if samplesheet_not_found :    
        #Create a new samplesheet for the new model since there are only one for different models
        samplesheet = Samplesheet(create_blank_samplesheet(dir, model, outputLocation))
        print(f"A {GREEN}new samplesheet{RESET} was created", flush=True)
        added_files = update_samplesheet(samplesheet, bar, telegram_bar)

    # Get the current date and time
    current_datetime = datetime.now()
    # Format the datetime to [DD/Mon/YYYY HH:MM:SS]
    formatted_datetime = current_datetime.strftime("%d/%b/%Y %H:%M:%S")   
    message = f"""Scan of `{dir}` at {formatted_datetime} added `{added_files}` files to `{samplesheet.file_path}`
    """
    telegram_send_bar(message)
    message = f"""{os.path.basename(samplesheet.file_path)} has now {len(samplesheet.get_files())} files
    """
    telegram_send_bar(message)
    if added_files>0:
        launch_run(samplesheet)