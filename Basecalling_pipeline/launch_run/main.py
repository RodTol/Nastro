import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from create_sbatch_file import *
from Basecalling_pipeline.subset_creation.config_file_api import *

sys.path.append("../subset_creation")
from runParameters import runParameters

if __name__ == "__main__":
    run_params = runParameters.from_file(sys.argv[1])
    
    if check_config_json_structure(run_params.config_path) == False:
        print(f"Json file for run {run_params.id} is not correct")
        sys.exit(1)
    
    sbatch_file = os.path.join(run_params.logs_dir, "script_" + run_params.id + ".sh")
    create_sbatch_file(run_params.config_path, sbatch_file) 
    
