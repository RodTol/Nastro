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

    config = ConfigFile(run_params.config_path)
    n_gpus = config.computing_resources.nodes_gpus
    total_gpus = int(n_gpus) if isinstance(n_gpus, str) else sum(int(x) for x in n_gpus)

    #TODO get this 4 from the max configuration json 
    ideal_size = run_params.ideal_size*total_gpus/4

    expected_time = 10*run_params.actual_size/ideal_size
    sleeping_time = (expected_time/5)*60
    #If too small set to 1 minutes
    if sleeping_time < 60:
        sleeping_time = 60

    telegram_send_bar("-----BASECALLING-RUN-----")

    message = f"""I am watching the run `{run_params.id}`
This run has a size of `{round(run_params.actual_size,2)} GB`
Resources: {total_gpus} GPUs
For a 10 minutes run we have an ideal size of `{round(ideal_size,2)} GB`
So the expected time is `{round(expected_time,2)} minutes`
"""
    telegram_send_message(message)
    telegram_send_message(f"I will send a message each `{round(sleeping_time, 2)}` s")

    original_target_file_indexes = [i for i,sample in enumerate(samplesheet.get_files()) if sample['basecalled']==run_params.id]
    start_size=len(original_target_file_indexes)

    bar = CustomPercentProgressBar(length=50,
                            left_limit='[',
                            right_limit=']',
                            head_repr='>',
                            empty_repr=' ',
                            filled_repr='=',
                            start=0,
                            scale_start=0,
                            scale_end=run_params.actual_size)
    
    processed_file_indexes_new = []
    processed_file_indexes_old = []

    telegram_send_bar(bar.progress_bar)
    target_file_indexes = original_target_file_indexes
    while len(target_file_indexes) > 0:
        sleep(sleeping_time)
        #Update
        samplesheet.data = samplesheet.read_file()
        target_file_indexes = [i for i,sample in enumerate(samplesheet.get_files()) if sample['basecalled']==run_params.id]
        current_size=len(target_file_indexes)

        processed_file_indexes_old = processed_file_indexes_new
        processed_file_indexes_new = [i for i in original_target_file_indexes if samplesheet.data["files"][i]['basecalled']==True]

        cycle_processed = [item for item in processed_file_indexes_new if item not in processed_file_indexes_old]
        print("File processati", [samplesheet.data["files"][i]["name"] for i in cycle_processed])
        
        message = f"""I processed in this cycle {len(cycle_processed)} files, so
{current_size} files are still being processed;
The batch is made of {start_size} files;
        """
        telegram_send_message(message)

        if (len(cycle_processed)>0):
            processed_bytes = 0
            for i in cycle_processed:
                processed_bytes += samplesheet.data["files"][i]['size(GB)']

            bar.increase(processed_bytes)
        telegram_send_bar(bar.progress_bar)

    message = f""" Basecalling was finished. This is the updated samplesheet
    """
    telegram_send_file(sys.argv[2], message)
