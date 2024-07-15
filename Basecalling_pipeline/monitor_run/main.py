import sys
import os
from time import sleep

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.config_file_api import *
from Basecalling_pipeline.subset_creation.runParameters import runParameters
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet

from bot_telegram import *
from progress_bar import *

if __name__ == "__main__":
    run_params = runParameters.from_file(sys.argv[1])
    samplesheet = Samplesheet(sys.argv[2])

    expected_time = run_params.actual_size*10/run_params.ideal_size
    sleeping_time = expected_time/100

    message = f"""I am watching the run `{run_params.id}`
This run has a size of `{round(run_params.actual_size,2)} GB`, an excepted one of `{round(run_params.ideal_size,2)} GB`
So the expected time is `{round(expected_time,2)}`
"""
    telegram_send_message(message)
    telegram_send_message(f"I will send a message each `{run_params.id}` seconds")

    target_file_indexes = [i for i,sample in enumerate(samplesheet.data) if sample['basecalled']==run_params.id]
    start_size=len(target_file_indexes)

    bar = CustomPercentProgressBar(length=50,
                            left_limit='[',
                            right_limit=']',
                            head_repr='>',
                            empty_repr=' ',
                            filled_repr='=',
                            start=0,
                            scale_start=0,
                            scale_end=run_params.actual_size)
    print(bar.progress_bar)

    processed_file_indexes_new = []
    processed_file_indexes_old = []
    while len(target_file_indexes) > 0:
        sleep(sleeping_time)
        #Update
        samplesheet.data = samplesheet.read_file()
        target_file_indexes = [i for i,sample in enumerate(samplesheet.data) if sample['basecalled']==run_params.id]
        current_size=len(target_file_indexes)

        processed_file_indexes_old = processed_file_indexes_new
        processed_file_indexes_new = [i for i,sample in enumerate(samplesheet.data) if sample['basecalled']==True]

        cycle_processed = [item for item in processed_file_indexes_new if item not in processed_file_indexes_old]
        print("File processati", cycle_processed)
        
        message = f""" I started with {start_size} files;
I processed in this cycle {len(cycle_processed)} files, so
{current_size} files are still being processed
        """
        telegram_send_message(message)

        if (len(cycle_processed)>0):
            processed_bytes = 0
            for i in cycle_processed:
                processed_bytes += samplesheet.data[i]['size(GB)']

            bar.increase(processed_bytes)
            print(bar.progress_bar)

