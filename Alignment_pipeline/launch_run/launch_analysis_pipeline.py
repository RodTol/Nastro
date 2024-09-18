# Copyright 2024 Area Science Park
# Author: Rodolfo Tolloi
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

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.pipelineInteract import Jenkins_trigger

if __name__ == "__main__":
    jenkins_parameter =  {
        "pathToSamplesheet": sys.argv[1],
        "RunId": sys.argv[2]
    }

    jenkins = Jenkins_trigger()
    jenkins.start_job('tolloi/Nastro/analysis_pipeline', 'manwe', jenkins_parameter)
