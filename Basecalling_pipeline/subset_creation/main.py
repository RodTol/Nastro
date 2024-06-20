import sys
import os
import hashlib
import datetime
from runParameters import runParameters
from mainParameters import mainParameters
from config_file_api import *
from resource_profiler import *
from subset_creator import Subsetter

def create_dir(path):
    try: 
        os.makedirs(path, exist_ok = True) 
        #print("Directory '%s' created successfully" % path) 
    except OSError as error: 
        print("Directory '%s' can not be created" % path)

def generate_short_hash(input_str):
    return hashlib.sha256(input_str.encode()).hexdigest()[:8]

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python3 main.py path/to/file.json path/to/input/root/dir path/to/output/root/dir path/to/logs/root/dir basecalling model")
        sys.exit(1)
    
    main_params = mainParameters(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    print(main_params)

    run_params = runParameters('','','','','')

    #Create batch hash identifier
    time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    run_params.id = generate_short_hash(time) + "_" + time

    #Create input dir for the run
    run_params.input_dir = os.path.join(main_params.input_dir, run_params.id)
    create_dir(run_params.input_dir)

    #Set basecalling model
    run_params.basecalling_model = main_params.basecalling_model

    #Set ideal size
    run_params.ideal_size = choose_ideal_size(run_params.basecalling_model)

    #Create the actual subset inside the input dir
    subsetter = Subsetter(main_params.samplesheet)
    run_subset, run_params.actual_size = subsetter.create_subset(run_params.id, target_size=run_params.ideal_size)
    run_params.create_run_input_symlinks(run_subset)

    #Create output dir for the run
    run_params.output_dir = os.path.join(main_params.output_dir, run_params.id)
    create_dir(run_params.output_dir)

    #Create logs dir for the run
    run_params.logs_dir = os.path.join(main_params.logs_dir, run_params.id)
    create_dir(run_params.logs_dir)

    #Create config file in run logs dir
    run_params.config_path = os.path.join(run_params.logs_dir, "config_" + run_params.id + ".json")
    run_config = ConfigFile(run_params.config_path)
    
    #Ready
    print(run_params)

    #Save the run_params and print it to file
    jenkins_build_id = os.environ.get('BUILD_ID')
    run_params_file_path = os.path.join(main_params.logs_dir, f"runParams_build_{jenkins_build_id}.txt")
    run_params.write_to_file(run_params_file_path)

    #Configure run_config
    #General
    run_config.general = General(run_config, "Run_" + run_params.id, "3:0:0 ")
    #Slurm
    run_slurm_output = os.path.join(run_params.logs_dir, "%x-%j.out")
    run_slurm_error = os.path.join(run_params.logs_dir, "%x-%j.err")
    run_config.slurm = Slurm(run_config, run_slurm_output , run_slurm_output, "script.sh")
    #Basecalling
    run_config.basecalling = Basecalling(run_config, run_params.basecalling_model, run_params.input_dir,
                                         run_params.output_dir, run_params.logs_dir, "supervisor.sh")
    #Resources
    #Calculate resources and then update the config file
    run_config.computing_resources = ResourceTuning(run_params, run_config).compute_resources()