# Copyright 2024 Rodolfo Tolloi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    all_files = os.listdir(dir)
    pod5_files = [Path(file) for file in all_files if file.endswith('.pod5')]
    # Get absolute paths for each .pod5 file
    pod5_files = [dir_path / file for file in pod5_files]
    pod5_files = [str(file.resolve()) for file in pod5_files]

    return pod5_files

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
    dir = samplesheet.get_metadata()["dir"]
    all_scanned_pod5_files = list_pod5(dir)
    
    added_files = 0

    for i,scanned_file_path in enumerate(all_scanned_pod5_files):
        if samplesheet.file_belongs_to_samplesheet(scanned_file_path):
            all_scanned_pod5_files.pop(i)
            #Increase beacuse already added
            if bar!=None:
                bar.increase(1)
                if i==len(all_scanned_pod5_files)-1:
                    telegram_bar.telegram_send_bar(bar.progress_bar)
        else: 
            parser = prepare_pod5_inspect_argparser()
            args = parser.parse_args(['debug', scanned_file_path])

            # Redirect stdout in order to have no prints
            sys.stdout = open(os.devnull, 'w')
            try :
                # Check if it is closed
                inspect_pod5(command=args.command, input_files=args.input_files)
            except Exception as exc:
                # This is how we handle this exception THAT IS NOT RAISEED
                sys.stdout = sys.__stdout__ 
                print(f"Failed to open file {scanned_file_path} due to {exc}", flush=True) 
            else:
                # But we must reset stdout to its default value every time
                sys.stdout = sys.__stdout__ 
                print('Added ', scanned_file_path , ' to the list', flush=True)
                if bar!=None:
                    #Increase beacuse new file
                    bar.increase(1)
                    telegram_bar.telegram_send_bar(bar.progress_bar)
                if samplesheet.add_file(create_samplesheet_entry(scanned_file_path)):
                    added_files = added_files + 1

    samplesheet.update_json_file()
    return added_files
