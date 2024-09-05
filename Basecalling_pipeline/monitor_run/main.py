import sys
import os
from time import sleep

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.config_file_api import *
from Basecalling_pipeline.subset_creation.runParameters import runParameters
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet

from bot_telegram import *

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
I will send a message each {round(sleeping_time, 2)} s
"""
    telegram_send_bar(message)

    original_target_file_indexes = [i for i,sample in enumerate(samplesheet.get_files()) if sample['basecalled']==run_params.id]
    start_size=len(original_target_file_indexes)    

    #TODO maybe a better tracking of the processing speed ?
    #maybe by looking at output dir ?
    target_file_indexes = original_target_file_indexes

    #Start the loop
    while len(target_file_indexes) > 0:
        sleep(sleeping_time)
        #Update
        samplesheet.data = samplesheet.read_file()
        #Get the ones that still needs to be processed
        target_file_indexes = [i for i,sample in enumerate(samplesheet.get_files()) if sample['basecalled']==run_params.id]
        target_current_size=len(target_file_indexes)
        #Get the ones processed in this cycle
        processed_file_indexes = [i for i in original_target_file_indexes if i not in target_file_indexes]
        print("File processati", [samplesheet.data["files"][i]["name"] for i in processed_file_indexes])
        
        message = f"""I processed in this cycle {len(processed_file_indexes)} files, so
{target_current_size} files are still being processed;
The batch was made of {start_size} files;
        """
        telegram_send_bar(message)

    message = f""" Basecalling was finished; This is the updated samplesheet"""
    telegram_send_file(sys.argv[2], message)
