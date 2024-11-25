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
import pod5
from pod5.tools.pod5_inspect import do_debug_command, do_read_command, do_reads_command, do_summary_command
from pod5.tools.utils import collect_inputs
from pod5.tools.parsers import prepare_pod5_inspect_argparser

def inspect_pod5(
    command: str, input_files: List[Path], recursive: bool = False, **kwargs
):
    """
    Determine which inspect command to run from the parsed arguments and run it.

    Rewrote by myself in order to throw an exception in case something went wrong
    (like in my case the file is yet to to be finished to be copied).
    """

    commands: Dict[str, Callable] = {
        "reads": do_reads_command,
        "read": do_read_command,
        "summary": do_summary_command,
        "debug": do_debug_command,
    }

    for idx, filename in enumerate(
        collect_inputs(input_files, recursive=recursive, pattern="*.pod5")
    ):
        try:
            reader = pod5.Reader(filename)
        except Exception as exc:
            print(f"Failed to open pod5 file: {filename}: {exc}", file=sys.stderr, flush=True)
            raise #ONLY DIFFERENCE

        kwargs["reader"] = reader
        kwargs["write_header"] = idx == 0
        commands[command](**kwargs)


def list_pod5(dir):
    dir_path = Path(dir)
    if not dir_path.is_dir():
        raise ValueError(f"The provided path '{dir}' is not a directory or does not exist.")
    
    pod5_files = [str(file.resolve()) for file in dir_path.iterdir() if file.is_file() and file.suffix == '.pod5']
    return pod5_files

def list_json(dir):
    all_files= os.listdir(dir)
    json_files = [file for file in all_files if file.endswith('.json')]
    json_files = [os.path.join(dir, file) for file in json_files]
    return json_files    

def is_same_samplesheet(path_to_samplesheet, dir, model, outputLocation, performAlign):
    samplesheet = Samplesheet(path_to_samplesheet)
    if Path(samplesheet.get_metadata()["dir"]).resolve() != Path(dir).resolve():
        print(f"{path_to_samplesheet} has a different dir")
        return False
    if samplesheet.get_metadata()["model"] != model:
        print(f"{path_to_samplesheet} has a different model")
        return False
    if Path(samplesheet.get_metadata()["outputLocation"]).resolve() != Path(outputLocation).resolve():
        print(f"{path_to_samplesheet} has a different outputLocation")
        return False    
    if samplesheet.get_metadata()["performAlign"] != performAlign:
        print(f"{path_to_samplesheet} has a different outputLocation")
        return False    
    return True

def create_blank_samplesheet(dir, model, outputLocation, performAlign):
    # Define the structure of the JSON data
    data = {
        "metadata": {
            "dir": dir,
            "model": model,
            "outputLocation": outputLocation,
            "performAlign": performAlign
        },
        "files": []
    }

    # Define the file name
    path = Path(dir)
    dir_name = path.name if path.is_dir() else path.parent.name
    print(performAlign, " ", type(performAlign), flush=True) 
    if performAlign==True:
        file_name = f"run_{dir_name}_aligned_{model.replace('.cfg', '').replace('.', '-')}.json"
    else:
        file_name = f"run_{dir_name}_{model.replace('.cfg', '').replace('.', '-')}.json"

    # Write the JSON data to the file
    file_path = path / file_name
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)    
    
    return file_path.resolve()

def update_samplesheet(samplesheet: Samplesheet, bar=None, telegram_bar=None):
    """
    Updates a samplesheet by scanning for new pod5 files and adding them if not already present
    
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
    # Get list of all pod5 files in directory
    all_scanned_pod5_files = list_pod5(dir)
    print(f"I found {len(all_scanned_pod5_files)} pod5 files in {dir}", flush=True)

    added_files = 0
    already_scanned_files = 0
    
    # Iterate through found pod5 files
    for i,scanned_file_path in enumerate(all_scanned_pod5_files):
        # Check if file is already in samplesheet
        if samplesheet.file_belongs_to_samplesheet(scanned_file_path):
            # Remove from list if already present
            all_scanned_pod5_files.pop(i)
            print(f"File {scanned_file_path} is already in the list", flush=True)
            already_scanned_files = already_scanned_files + 1
            # Update progress bars for existing files
            if bar!=None:
                bar.increase(1)
                if i==len(all_scanned_pod5_files)-1:
                    telegram_bar.telegram_send_bar(bar.progress_bar)
        else: 
            # For new files, prepare to inspect the pod5 file
            parser = prepare_pod5_inspect_argparser()
            args = parser.parse_args(['debug', scanned_file_path])

            # Temporarily redirect stdout to suppress output
            sys.stdout = open(os.devnull, 'w')
            try :
                # Try to inspect the pod5 file to verify it's complete/valid
                inspect_pod5(command=args.command, input_files=args.input_files)
            except Exception as exc:
                # Handle case where file can't be opened (e.g. still being written)
                sys.stdout = sys.__stdout__ 
                print(f"Failed to open file {scanned_file_path} due to {exc}", flush=True) 
                if bar!=None:
                    # Update progress even for failed files
                    bar.increase(1)  
                    telegram_bar.telegram_send_bar(bar.progress_bar)              
            else:
                # File inspection succeeded, reset stdout to its default value every time
                sys.stdout = sys.__stdout__ 
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
    print(f"Added {added_files} new files to the samplesheet", flush=True)
    print(f"Already scanned {already_scanned_files} files", flush=True)
    samplesheet.update_json_file()
    return added_files
