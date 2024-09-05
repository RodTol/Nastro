import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet
from Basecalling_pipeline.monitor_run.bot_telegram import telegram_send_bar
from Basecalling_pipeline.monitor_run.bot_telegram import telegram_send_file


if __name__ == "__main__":
    samplehseet = Samplesheet(sys.argv[1])
    id = sys.argv[2]
    status = sys.argv[3]
    path_to_report = sys.argv[4]

    if status=="Correct":
        for i,file in enumerate(samplehseet.get_files()):
            if file["aligned"] == id:
                samplehseet.data["files"][i]["aligned"] = True
    else:
        for i,file in enumerate(samplehseet.get_files()):
            if file["aligned"] == id:
                samplehseet.data["files"][i]["aligned"] = "Failed"
                
    samplehseet.update_json_file()
    
    if status=="Correct":
        telegram_send_bar(f"Run {id} has succesfully completed the alignment")
    else:
        telegram_send_bar(f"Something went wrong in run {id}")
    
    telegram_send_file(samplehseet.file_path, "This is the updated samplesheet")
    if path_to_report: telegram_send_file(path_to_report, "and a basic report on the alignment")