#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"

import os
import sys
from datetime import datetime


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.runParameters import runParameters
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet
from Basecalling_pipeline.subset_creation.config_file_api import ConfigFile
from Basecalling_pipeline.monitor_run.bot_telegram import telegram_send_bar
from Basecalling_pipeline.subset_creation.resource_profiler import IDEAL_RUN_TIME

from al_config_file_api import *
from profiler import ResourceTuner

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 main.py path/to/samplesheet.json path/to/runparams path/to/merged_fastq")
        sys.exit(1)

    samplesheet = Samplesheet(sys.argv[1])
    run_params = runParameters.from_file(sys.argv[2])
    merged_file = sys.argv[3]

    #Get merged file's size
    size = os.path.getsize(merged_file)/(1024**3)
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
    #TODO absolute path
    supervisor_script_path = '/u/area/jenkins_onpexp/Nastro/Alignment_pipeline/launch_run/al_instructions.sh'
    al_run_config.slurm = Slurm(al_run_config, run_slurm_output , run_slurm_error, supervisor_script_path)

    #TODO should ref_genome be a pipeline parameters, maybe even part of the samplesheet as it is the model ?
    ref_genome = '/orfeo/cephfs/scratch/area/jenkins_onpexp/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna'
    output_file = f"{bc_run_config.basecalling.output_dir}/run_{run_params.id}.bam"

    al_run_config.alignment = Alignment(al_run_config, merged_file, output_file,
                                         run_params.logs_dir, ref_genome, "")
    
    resourcetuner = ResourceTuner(run_params, al_run_config, size)
    al_run_config.computing_resources = resourcetuner.compute_resources()

    normalized_ideal_size = resourcetuner.ideal_size*float(al_run_config.computing_resources.node_cpus)/32
    expected_time = IDEAL_RUN_TIME*size/normalized_ideal_size

    # Get the current date and time
    current_datetime = datetime.now()
    # Format the datetime to [DD/Mon/YYYY HH:MM:SS]
    formatted_datetime = current_datetime.strftime("%d/%b/%Y %H:%M:%S")   
    message = f"""Merging completed at {formatted_datetime}
I am watching the AL-run `{run_params.id}`
The fastq file has a size of `{round(size,2)} GB`
Resources: {al_run_config.computing_resources.node_cpus} CPUs
For a {IDEAL_RUN_TIME} minutes run we have an ideal size of `{normalized_ideal_size} GB`
So the expected time is `{round(expected_time,2)} minutes`
"""
    telegram_send_bar(message)        