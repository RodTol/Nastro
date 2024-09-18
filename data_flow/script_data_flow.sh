#!/bin/bash
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

#SBATCH --job-name=data_flow
#SBATCH --time=06:00:00
#SBATCH --output=/u/area/jenkins_onpexp/Pipeline_long_reads/data_flow/data_flow.out
#SBATCH --error=/u/area/jenkins_onpexp/Pipeline_long_reads/data_flow/data_flow.err
#SBATCH -A lage
#SBATCH -p EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=10GB

source=$1
dest=$2

python3 /u/area/jenkins_onpexp/BC-pipelines/simulation-pipeline/utility/data_flow_emulator.py $source $dest