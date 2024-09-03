import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.runParameters import runParameters
from Alignment_pipeline.setupRun.al_config_file_api import check_config_json_structure
from create_sbatch_file import create_sbatch_file

if __name__ == "__main__":
    run_params = runParameters.from_file(sys.argv[1])
    
    if check_config_json_structure(run_params.al_config_path) == False:
        print(f"Json file for run {run_params.id} is not correct")
        sys.exit(1)    
    
    sbatch_file = os.path.join(run_params.logs_dir, "al_script_" + run_params.id + ".sh")
    create_sbatch_file(run_params.al_config_path, sbatch_file)