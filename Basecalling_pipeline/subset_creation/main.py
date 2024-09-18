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

import sys
import os
import hashlib
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet
from runParameters import runParameters
from mainParameters import mainParameters
from config_file_api import *
from resource_profiler import *
from subset_creator import Subsetter
from pipelineInteract import Jenkins_trigger

def create_dir(path):
    try: 
        os.makedirs(path, exist_ok = True) 
        #print("Directory '%s' created successfully" % path) 
    except OSError as error: 
        print("Directory '%s' can not be created" % path)

def generate_short_hash(input_str):
    return hashlib.sha256(input_str.encode()).hexdigest()[:8]

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 main.py path/to/samplesheet.json path/to/input/root/dir path/to/output/root/dir path/to/logs/root/dir")
        sys.exit(1)
    
    samplesheet = Samplesheet(sys.argv[1])
    bc_model = samplesheet.get_metadata()["model"]

    main_params = mainParameters(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], bc_model)
    print(main_params)

    run_params = runParameters('','','','','')
    jenkins_build_id = os.environ.get('BUILD_NUMBER_LOCAL')

    #Create batch hash identifier
    time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    run_params.id = generate_short_hash(time) + "_" + time

    #Set basecalling model
    run_params.basecalling_model = main_params.basecalling_model

    #Set ideal size
    run_params.ideal_size = choose_ideal_size(run_params.basecalling_model)

    #Create the actual subset
    subsetter = Subsetter(main_params.samplesheet)
    run_subset, run_params.actual_size = subsetter.create_subset(run_params.id, target_size=run_params.ideal_size)
    
    if (len(run_subset)==0 and run_params.actual_size==0) :
        jenkins_parameter =  {
             "pathToDir": samplesheet.get_metadata()["dir"],
             "basecallingModel" : samplesheet.get_metadata()["model"],
             "outputLocation": samplesheet.get_metadata()["outputLocation"]
         }

        jenkins = Jenkins_trigger()
        jenkins.start_job('tolloi/Pipeline_long_reads/FileScanner', 'akira', jenkins_parameter)
        jenkins.stop_job('Nastro/job/basecalling_pipeline/', jenkins_build_id)
        sys.exit(0)

    #Create input dir for the run
    run_params.input_dir = os.path.join(main_params.input_dir, run_params.id)
    create_dir(run_params.input_dir)

    #Create the symlinks inside the input dir
    run_params.create_run_input_symlinks(run_subset)

    #Create output dir for the run
    run_params.output_dir = os.path.join(main_params.output_dir, run_params.id)
    create_dir(run_params.output_dir)
    
    pass_output_dir = os.path.join(run_params.output_dir, "pass")
    fail_output_dir = os.path.join(run_params.output_dir, "fail")
    create_dir(pass_output_dir)
    create_dir(fail_output_dir)

    #Create logs dir for the run
    run_params.logs_dir = os.path.join(main_params.logs_dir, run_params.id)
    create_dir(run_params.logs_dir)

    #Create config file in run logs dir
    run_params.config_path = os.path.join(run_params.logs_dir, "config_" + run_params.id + ".json")
    run_config = ConfigFile(run_params.config_path)
    
    #Ready
    print(run_params)

    #Save the run_params and print it to file
    run_params_file_path = os.path.join(main_params.logs_dir, f"runParams_build_{jenkins_build_id}.txt")
    run_params.write_to_file(run_params_file_path)

    #Configure run_config
    #General
    run_config.general = General(run_config, "Run_" + run_params.id, "3:0:0 ")
    #Slurm
    run_slurm_output = os.path.join(run_params.logs_dir, "%x-%j.out")
    run_slurm_error = os.path.join(run_params.logs_dir, "%x-%j.err")
    run_config.slurm = Slurm(run_config, run_slurm_output , run_slurm_error, "${HOME}/Nastro/Basecalling_pipeline/launch_run/instructions.sh")
    #Basecalling
    home_dir = os.getenv('HOME')
    supervisor_script_path = os.path.join(home_dir, 'Nastro/Basecalling_pipeline/launch_run/supervisor.sh')

    # Assign the constructed path to your attribute
    run_config.basecalling = Basecalling(run_config, run_params.basecalling_model, run_params.input_dir,
                                        run_params.output_dir, run_params.logs_dir, supervisor_script_path)
    #Resources
    #Calculate resources and then update the config file
    run_config.computing_resources = ResourceTuning(run_params, run_config).compute_resources()