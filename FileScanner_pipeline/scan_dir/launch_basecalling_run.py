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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.pipelineInteract import Jenkins_trigger
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet

def launch_run(samplesheet: Samplesheet):
    #Create input, logs, output dirs
    input_path = os.path.join(samplesheet.get_metadata()["outputLocation"], 'input')
    logs_path = os.path.join(samplesheet.get_metadata()["outputLocation"], 'logs')
    output_path = os.path.join(samplesheet.get_metadata()["outputLocation"], 'output')

    os.makedirs(input_path, exist_ok=True)
    os.makedirs(logs_path, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)

    jenkins_parameter =  {
            "pathToSamplesheet": samplesheet.file_path,
            "pathToInputDir" : input_path,
            "pathToOutputDir": output_path,
            "pathToLogsDir": logs_path,
            "RUN_TESTING_CLEANUP": False
        }    
    
    jenkins = Jenkins_trigger()
    jenkins.start_job('tolloi/Nastro/basecalling_pipeline', 'kuribo', jenkins_parameter)