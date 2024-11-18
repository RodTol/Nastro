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
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet
from Basecalling_pipeline.samplesheet_check.samplesheet_api import create_samplesheet_entry
from Basecalling_pipeline.monitor_run.bot_telegram import Telegram_bar

from pathlib import Path
from typing import Callable, Dict, List


def list_fast5(dir):
    dir_path = Path(dir)
    all_files = os.listdir(dir)
    fast5_files = [Path(file) for file in all_files if file.endswith('.fast5')]
    # Get absolute paths for each .fast5 file
    fast5_files = [dir_path / file for file in fast5_files]
    fast5_files = [str(file.resolve()) for file in fast5_files]

    return fast5_files    

def list_json(dir):
    all_files= os.listdir(dir)
    json_files = [file for file in all_files if file.endswith('.json')]
    json_files = [os.path.join(dir, file) for file in json_files]
    return json_files    

#TODO: should I not check also the "outputLocation" ?
def is_same_samplesheet(path_to_samplesheet, dir, model, outputLocation):
    samplesheet = Samplesheet(path_to_samplesheet)
    if Path(samplesheet.get_metadata()["dir"]).resolve() != Path(dir).resolve():
        print(f"{path_to_samplesheet} has a different dir")
        return False
    if samplesheet.get_metadata()["model"] != model:
        print(f"{path_to_samplesheet} has a different model")
        return False
    if samplesheet.get_metadata()["outputLocation"] != outputLocation:
        print(f"{path_to_samplesheet} has a different outputLocation")
        return False    
    return True

def create_blank_samplesheet(dir, model, outputLocation):
    # Define the structure of the JSON data
    data = {
        "metadata": {
            "dir": dir,
            "model": model,
            "outputLocation": outputLocation
        },
        "files": []
    }

    # Define the file name
    path = Path(dir)
    dir_name = path.name if path.is_dir() else path.parent.name
    file_name = f"run_{dir_name}_{model.replace('.cfg', '').replace('.', '-')}.json"

    # Write the JSON data to the file
    file_path = path / file_name
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)    
    
    return file_path.resolve()

def update_samplesheet(samplesheet: Samplesheet, bar=None, telegram_bar=None):
    """
    Updates a samplesheet by scanning for new fast5 files and adding them if not already present
    
    Args:
        samplesheet: Samplesheet object to update
        bar: Optional progress bar object
        telegram_bar: Optional Telegram progress bar object
    
    Returns:
        Number of new files added to the samplesheet
    """
    # Could lose updates if another program writes to the file between read_file() and update_json_file() calls
    
    # Get directory from samplesheet metadata
    dir = samplesheet.get_metadata()["dir"]
    # Get list of all fast5 files in directory
    all_scanned_fast5_files = list_fast5(dir)
    
    added_files = 0
    
    # Iterate through found fast5 files
    for i,scanned_file_path in enumerate(all_scanned_fast5_files):
        # Check if file is already in samplesheet
        if samplesheet.file_belongs_to_samplesheet(scanned_file_path):
            # Remove from list if already present
            all_scanned_fast5_files.pop(i)
            # Update progress bars for existing files
            if bar!=None:
                bar.increase(1)
                if i==len(all_scanned_fast5_files)-1:
                    telegram_bar.telegram_send_bar(bar.progress_bar)
        else: 
            # RACE CONDITION: Another program could modify the file between these operations
            samplesheet.data = samplesheet.read_file()
            print('Added ', scanned_file_path , ' to the list', flush=True)    
            if bar!=None:
                # Update progress for new file
                bar.increase(1)
                telegram_bar.telegram_send_bar(bar.progress_bar)        
            # Create and add new entry to samplesheet
            if samplesheet.add_file(create_samplesheet_entry(scanned_file_path)):
                # Update the samplesheet since some operation my have been performed in this time
                added_files = added_files + 1
                samplesheet.update_json_file()

    # Final update of samplesheet file
    samplesheet.update_json_file()
    return added_files