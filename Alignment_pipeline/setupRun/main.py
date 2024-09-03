import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.runParameters import runParameters
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet
from Basecalling_pipeline.subset_creation.config_file_api import ConfigFile

from al_config_file_api import *
from profiler import ResourceTuner

def create_dir(path):
    try: 
        os.makedirs(path, exist_ok = True) 
        #print("Directory '%s' created successfully" % path) 
    except OSError as error: 
        print("Directory '%s' can not be created" % path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 main.py path/to/samplesheet.json path/to/runparams path/to/merged_fastq")
        sys.exit(1)

    samplesheet = Samplesheet(sys.argv[1])
    run_params = runParameters.from_file(sys.argv[2])
    merged_file = sys.argv[3]

    bam_output_dir = os.path.join(run_params.output_dir, "bam")
    create_dir(bam_output_dir)

    #Get merged file's size
    size = os.path.getsize(merged_file)
    print(f"Size of the merged file: {size}", flush=True)
    
    #Create config file
    run_params.al_config_path = os.path.join(run_params.logs_dir, "al_config_" + run_params.id + ".json")
    al_run_config = AlConfigFile(run_params.al_config_path)

    print(run_params)
    #Save the run_params and print it to file
    run_params.write_to_file(sys.argv[2])

    #Add values to config params
    bc_run_config = ConfigFile(run_params.config_path)
    al_run_config.general = bc_run_config.general

    run_slurm_output = os.path.join(run_params.logs_dir, "%x-%j_al.out")
    run_slurm_error = os.path.join(run_params.logs_dir, "%x-%j_al.err")
    al_run_config.slurm = Slurm(al_run_config, run_slurm_output , run_slurm_error, "")

    al_run_config.alignment = Alignment(al_run_config, merged_file,
                                         f"{bam_output_dir}/run_{run_params.id}.bam", run_params.logs_dir, "")
    
    #al_run_config.computing_resources = ResourceTuner().compute_resources()
    
    #Create sbatch file for the run in the logs dir






