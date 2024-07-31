import sys
import os

from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet
from pathlib import Path
from typing import Callable, Dict, List
import pod5
from pod5.tools.pod5_inspect import do_debug_command, do_read_command, do_reads_command, do_summary_command
from pod5.tools.utils import collect_inputs
from pod5.tools.parsers import prepare_pod5_inspect_argparser

def list_pod5(dir):
    all_files= os.listdir(dir)
    pod5_files = [file for file in all_files if file.endswith('.pod5')]
    return pod5_files    

def list_json(dir):
    all_files= os.listdir(dir)
    json_files = [file for file in all_files if file.endswith('.json')]
    return json_files    

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
            print(f"Failed to open pod5 file: {filename}: {exc}", file=sys.stderr)
            raise #ONLY DIFFERENCE

        kwargs["reader"] = reader
        kwargs["write_header"] = idx == 0
        commands[command](**kwargs)


def create_samplesheet(dir):
    #Scan for other samplesheet
    list_json(dir)