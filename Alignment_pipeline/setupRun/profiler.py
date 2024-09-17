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

import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.runParameters import runParameters
from al_config_file_api import ComputingResources
from al_config_file_api import AlConfigFile


cpus_32_speed = 0.02987 # in GB/s
IDEAL_RUN_TIME = 10 
IDEAL_SIZE_GB = cpus_32_speed*IDEAL_RUN_TIME*60 #around 17.9 GB


class ResourceTuner:

    def __init__ (self, run_params, al_run_config, merged_fastq_size):
        if not isinstance(run_params, runParameters):
            raise TypeError("run_params must be an instance of runParameters")
        self.run_params = run_params
        
        if not isinstance(al_run_config, AlConfigFile):
            raise TypeError("run_config must be an instance of AlConfigFile")
        self.al_run_config = al_run_config        

        self.fastq_size = merged_fastq_size
        self.ideal_size = float(IDEAL_SIZE_GB)

    #TODO path are for orfeo
    def compute_resources(self):
        if self.fastq_size >= IDEAL_SIZE_GB:
            print(f"Ideal size: {IDEAL_SIZE_GB}; actual size: {self.fastq_size:.2f}")
            print("Using profile 1")
            
            with open('/u/area/jenkins_onpexp/Pipeline_long_reads/Alignment_pipeline/setupRun/computing_profiles/profile1.json', 'r') as file:
                profile = json.load(file)

            return ComputingResources(self.al_run_config, profile["node_queue"],
                                      profile["node_name"], profile["node_cpus"],
                                      profile["node_mem"])          
        elif self.fastq_size >= IDEAL_SIZE_GB/2:
            print(f"Ideal size: {IDEAL_SIZE_GB}; actual size: {self.fastq_size:.2f}")
            print("Using profile 2")
            
            with open('/u/area/jenkins_onpexp/Pipeline_long_reads/Alignment_pipeline/setupRun/computing_profiles/profile2.json', 'r') as file:
                profile = json.load(file)

            return ComputingResources(self.al_run_config, profile["node_queue"],
                                      profile["node_name"], profile["node_cpus"],
                                      profile["node_mem"])
        else:
            print(f"Ideal size: {IDEAL_SIZE_GB}; actual size: {self.fastq_size:.2f}")
            print("Using profile 3")
            
            with open('/u/area/jenkins_onpexp/Pipeline_long_reads/Alignment_pipeline/setupRun/computing_profiles/profile3.json', 'r') as file:
                profile = json.load(file)

            return ComputingResources(self.al_run_config, profile["node_queue"],
                                      profile["node_name"], profile["node_cpus"],
                                      profile["node_mem"])                 