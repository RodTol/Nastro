import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Basecalling_pipeline.subset_creation.config_file_api import *
from Basecalling_pipeline.subset_creation.runParameters import runParameters
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet

from bot_telegram import *

if __name__ == "__main__":
    run_params = runParameters.from_file(sys.argv[1])
    samplesheet = Samplesheet(sys.argv[2])

    expected_time = run_params.actual_size*10/run_params.ideal_size

    message = f"""I am watching the run {run_params.id}
    This run has a size of {run_params.actual_size}, an excepted one of {run_params.ideal_size}
    So the expected time is {expected_time}
    """
    telegram_send_message(message)
    
