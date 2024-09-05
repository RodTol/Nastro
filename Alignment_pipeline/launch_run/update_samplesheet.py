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

    for file in samplehseet.get_files():
        if file["aligned"] == id:
            file["aligned"] = status
    
    samplehseet.update_json_file()
    
    if status=="True":
        telegram_send_bar(f"Run {id} has succesfully completed the alignment")
    else:
        telegram_send_bar(f"Something went wrong in run {id}")
    
    telegram_send_file(samplehseet.file_path, "This is the updated samplesheet")