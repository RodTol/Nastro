#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet
from Basecalling_pipeline.monitor_run.bot_telegram import telegram_send_bar
from Basecalling_pipeline.monitor_run.bot_telegram import telegram_send_file


if __name__ == "__main__":
    samplesheet = Samplesheet(sys.argv[1])
    id = sys.argv[2]
    status = sys.argv[3]
    path_to_report = sys.argv[4]
    #TODO: maybe here I need to update and read each time?
    if status=="Correct":
        telegram_send_bar(f"Run {id} has succesfully completed the alignment")
        for entry in samplesheet.get_files():
            if entry["run_id"] == id:
                entry["aligned"] = True      
                samplesheet.update_json_file()
    else:
        telegram_send_bar(f"Something went wrong in run {id}")
        for entry in samplesheet.get_files():
            if entry["run_id"] == id:
                entry["aligned"] = "Failed"    
                samplesheet.update_json_file()

    samplesheet.update_json_file()

    telegram_send_file(samplesheet.file_path, "This is the updated samplesheet")
    if path_to_report: telegram_send_file(path_to_report, "and a basic report on the alignment")