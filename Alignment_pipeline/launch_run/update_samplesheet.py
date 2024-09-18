# Copyright 2024 Area Science Park
# Author: Rodolfo Tolloi
#
# Licensed under the Apache License, Version 2.0 (the "License");# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

    if status=="Correct":
        telegram_send_bar(f"Run {id} has succesfully completed the alignment")
        for entry in samplesheet.get_files():
            if entry["run_id"] == id:
                entry["aligned"] = True      
    else:
        telegram_send_bar(f"Something went wrong in run {id}")
        for entry in samplesheet.get_files():
            if entry["run_id"] == id:
                entry["aligned"] = "Failed"    

    samplesheet.update_json_file()

    telegram_send_file(samplesheet.file_path, "This is the updated samplesheet")
    if path_to_report: telegram_send_file(path_to_report, "and a basic report on the alignment")