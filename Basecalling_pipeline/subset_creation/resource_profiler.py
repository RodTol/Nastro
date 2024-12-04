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
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.runParameters import runParameters
from Basecalling_pipeline.subset_creation.config_file_api import ComputingResources
from Basecalling_pipeline.subset_creation.config_file_api import ConfigFile

# https://community.nanoporetech.com/requirements_documents/promethion-it-reqs.pdf?from=support
conversion_rate_Gbases_to_GB = 7 
#https://aws.amazon.com/blogs/hpc/benchmarking-the-oxford-nanopore-technologies-basecallers-on-aws/
fast_a100_speed_GB = float('1.63e-02')*conversion_rate_Gbases_to_GB
hac_a100_speed_GB = float('6.58e-03')*conversion_rate_Gbases_to_GB
sup_a100_speed_GB = float('1.24e-03')*conversion_rate_Gbases_to_GB

fast_v100_speed_GB = float('1.18e-02')*conversion_rate_Gbases_to_GB
hac_v100_speed_GB = float('2.01e-03')*conversion_rate_Gbases_to_GB
sup_v100_speed_GB = float('3.79e-04')*conversion_rate_Gbases_to_GB

#TODO IMPORTANT maybe make this time an input from config file ?
IDEAL_RUN_TIME = 30
#For 2 nodes with 4 dgx that will take IDEAL_RUN_TIME mins
FAST_IDEAL_SIZE_GB = 8*fast_a100_speed_GB*IDEAL_RUN_TIME*60
HAC_IDEAL_SIZE_GB = 8*hac_a100_speed_GB*IDEAL_RUN_TIME*60
SUP_IDEAL_SIZE_GB = 8*sup_a100_speed_GB*IDEAL_RUN_TIME*60


def choose_ideal_size(model):
    # Check for the keywords in the string and return the corresponding size
    #speeds = ['fast', 'hac', 'sup'] 
    #selected_speed = [model.find(speed) for speed in speeds]
    #print(model)
    if 'fast' in model.lower():
        print('Target size for FAST model')
        return FAST_IDEAL_SIZE_GB
    elif 'hac' in model.lower():
        print('Target size for HAC model')
        return HAC_IDEAL_SIZE_GB
    elif 'sup' in model.lower():
        print('Target size for SUP model')
        return SUP_IDEAL_SIZE_GB
    else:
        print(f"Using default size! {model} was not recognized\n Using HAC SIZE")
        return HAC_IDEAL_SIZE_GB  

def count_pod5_files(directory):
    count = 0
    for filename in os.listdir(directory):
        if filename.endswith(".pod5") and os.path.isfile(os.path.join(directory, filename)):
            count += 1
    return count

def split_number(n):
    part1 = n // 2
    part2 = n - part1
    return part1, part2

class ResourceTuning:
    '''
    This object will check if the paramters for a run are configured
    in optimal way. By default each model will arrive with a given ideal_size
    and a actual size. Based on the difference of this, it will recalculate the
    resources
    '''
    def __init__ (self, run_params, run_config):
        '''
        I need the params, and the config file in order to update
        immediatly the json file of the config
        '''
        if not isinstance(run_params, runParameters):
            raise TypeError("run_params must be an instance of runParameters")
        self.run_params = run_params
        
        if not isinstance(run_config, ConfigFile):
            raise TypeError("run_config must be an instance of ConfigFile")
        self.run_config = run_config

    def _length_of_subset(self):
        '''
        Read the length of the subset (maybe this function does not belong here
        but for now it does)
        '''
        dir = self.run_params.input_dir
        return count_pod5_files(dir)


    # def compute_resources(self):
    #     '''
    #     For the given run_params, return a ComputingResources object. profile 1 is the weakest profile
    #     while 4_4 is the strongest profile. The profiles are based on the number of nodes and the number of
    #     gpus assigned to it
    #     '''
    #     subset_length = self._length_of_subset()
    #     base_profile_path = '/u/area/jenkins_onpexp/Nastro/Basecalling_pipeline/subset_creation/computing_profiles'

    #     #TODO maybe add DGX status to be sure what profile is better ?
    #     profiles = [
    #         (self.run_params.ideal_size, f'{base_profile_path}/profile4_4.json'),
    #         (self.run_params.ideal_size/1.5, f'{base_profile_path}/profile4.json'),
    #         (self.run_params.ideal_size/2, f'{base_profile_path}/profile2_2.json'),
    #         (self.run_params.ideal_size/4, f'{base_profile_path}/profile2.json'),
    #         (0, f'{base_profile_path}/profile1.json'),
    #     ]

    #     for size_threshold, profile_path in profiles:
    #         if self.run_params.actual_size >= size_threshold:
    #             print(f"Using profile {profile_path}")
    #             with open(profile_path, 'r') as file:
    #                 profile = json.load(file)

    #             if len(profile["nodes_queue"]) >= 2:
    #                 size1, size2 = split_number(subset_length)                
    #                 profile["batch_size_list"] = [size1, size2]
    #             else:
    #                 profile["batch_size_list"] = [subset_length]

    #             return ComputingResources(
    #                 self.run_config, profile["index_host"], profile["port"], profile["nodes_queue"],
    #                 profile["nodes_list"], profile["nodes_ip"], profile["nodes_cpus"], profile["nodes_mem"],
    #                 profile["nodes_gpus"], profile["gpus"], profile["batch_size_list"]
    #            )
            
    def compute_resources(self):
        '''
        BENCHMARK VERSION of the function for fixed profile 
        '''
        subset_length = self._length_of_subset()
        profile_path = '/u/area/jenkins_onpexp/Nastro/Basecalling_pipeline/subset_creation/computing_profiles/profile1.json'

        with open(profile_path, 'r') as file:
            profile = json.load(file)

        if len(profile["nodes_queue"]) >= 2:
            size1, size2 = split_number(subset_length)                
            profile["batch_size_list"] = [size1, size2]
        else:
            profile["batch_size_list"] = [subset_length]

        return ComputingResources(
            self.run_config, profile["index_host"], profile["port"], profile["nodes_queue"],
            profile["nodes_list"], profile["nodes_ip"], profile["nodes_cpus"], profile["nodes_mem"],
            profile["nodes_gpus"], profile["gpus"], profile["batch_size_list"]
        )
