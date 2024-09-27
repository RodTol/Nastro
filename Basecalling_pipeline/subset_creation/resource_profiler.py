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

#TODO maybe make this time an input from config file ?
IDEAL_RUN_TIME = 20 
#For 2 nodes with 2 dgx that will take IDEAL_RUN_TIME mins
FAST_IDEAL_SIZE_GB = 4*fast_a100_speed_GB*IDEAL_RUN_TIME*60
HAC_IDEAL_SIZE_GB = 4*hac_a100_speed_GB*IDEAL_RUN_TIME*60
SUP_IDEAL_SIZE_GB = 4*sup_a100_speed_GB*IDEAL_RUN_TIME*60


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

    def compute_resources(self):
        '''
        For the given run_params return a ComputingResources object
        '''
        subset_length = self._length_of_subset()
        #sprint("Subset Length: ", subset_length)
        #Standard set of resources
        if self.run_params.actual_size >= self.run_params.ideal_size:
            print("Using profile 1")
            #TODO path and automatize splitting (count how many nodes I have and distribute files)
            with open('/u/area/jenkins_onpexp/Nastro/Basecalling_pipeline/subset_creation/computing_profiles/profile0.json', 'r') as file:
                profile = json.load(file)

            size1, size2 = split_number(subset_length)                
            profile["batch_size_list"] = [size1, size2]

            return ComputingResources(self.run_config, profile["index_host"], profile["port"], profile["nodes_queue"],
                                                        profile["nodes_list"], profile["nodes_ip"], profile["nodes_cpus"], 
                                                        profile["nodes_mem"], profile["nodes_gpus"], profile["gpus"],
                                                        profile["batch_size_list"])
        #half the ideal size --> one node 2 dgx (half the resources)
        elif self.run_params.actual_size >= self.run_params.ideal_size/2:
            print("Using profile 2")
            with open('/u/area/jenkins_onpexp/Nastro/Basecalling_pipeline/subset_creation/computing_profiles/profile2.json', 'r') as file:
                profile = json.load(file)

            return ComputingResources(self.run_config, profile["index_host"], profile["port"], profile["nodes_queue"],
                                                        profile["nodes_list"], profile["nodes_ip"], profile["nodes_cpus"], 
                                                        profile["nodes_mem"], profile["nodes_gpus"], profile["gpus"],
                                                        [subset_length])   
        #for now less than a quarter will use one a100. Maybe for very very less use v100
        else: 
            print("Using profile 3")            
            with open('/u/area/jenkins_onpexp/Nastro/Basecalling_pipeline/subset_creation/computing_profiles/profile3.json', 'r') as file:
                profile = json.load(file)

            return ComputingResources(self.run_config, profile["index_host"], profile["port"], profile["nodes_queue"],
                                                        profile["nodes_list"], profile["nodes_ip"], profile["nodes_cpus"], 
                                                        profile["nodes_mem"], profile["nodes_gpus"], profile["gpus"],
                                                        [subset_length])             