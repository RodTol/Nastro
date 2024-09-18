#!/bin/bash
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

#SBATCH --job-name=Monitor
#SBATCH --time=3:0:0
#SBATCH --partition=EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=1
#SBATCH --output=monitor.out
#SBATCH --error=monitor.err

pathToSamplesheet=$1
RUN_PARAMS_PATH=$2

source ~/python_venvs/orfeo_telegram_on_epyc/bin/activate

#python3 /u/area/jenkins_onpexp/LTS_tolloi/Orfeo_bot/main.py ${pathToSamplesheet} &
#pid=$!

deactivate

python3 ${HOME}/Nastro/Basecalling_pipeline/monitor_run/main.py ${RUN_PARAMS_PATH} ${pathToSamplesheet} 

# Kill the Python process
#kill $python_pid

