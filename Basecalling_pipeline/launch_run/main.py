# Copyright 2024 Rodolfo Tolloi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
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