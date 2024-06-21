import pytest
import json
import os
from Basecalling_pipeline.subset_creation.runParameters import runParameters
from Basecalling_pipeline.subset_creation.config_file_api import *
from Basecalling_pipeline.subset_creation.resource_profiler import *

@pytest.fixture
def correct_structure():
    with open('test_files/config_correct.json', 'r') as file:
        return json.load(file)

def compare_structures(correct, to_check):
    """
    Recursively compare the structure of two dictionaries.
    """
    if isinstance(correct, dict) and isinstance(to_check, dict):
        if set(correct.keys()) != set(to_check.keys()):
            return False
        return all(compare_structures(correct[key], to_check[key]) for key in correct)
    return True

def test_structure(correct_structure):
    run_params = runParameters.from_file('test_files/test_run_params.json')
    run_config = ConfigFile('test_files/config_tmp.json')
    #General
    run_config.general = General(run_config, "Run_" + run_params.id, "3:0:0 ")
    #Slurm
    run_slurm_output = os.path.join(run_params.logs_dir, "%x-%j.out")
    run_slurm_error = os.path.join(run_params.logs_dir, "%x-%j.err")
    run_config.slurm = Slurm(run_config, run_slurm_output , run_slurm_error, "script.sh")
    #Basecalling
    run_config.basecalling = Basecalling(run_config, run_params.basecalling_model, run_params.input_dir,
                                         run_params.output_dir, run_params.logs_dir, "supervisor.sh")
    #Resources
    #Calculate resources and then update the config file
    run_config.computing_resources = ComputingResources(run_config, "0", ["DGX","DGX"], ["dgx001", "dgx002"],
                                                        ["10.128.2.161", "10.128.2.162"], ["64, 64"], 
                                                        ["200GB", "200GB"], ["2", "2"], ["cuda:all", "cuda:all"],
                                                        ["10", "10"])
    
    # Check if the structures match
    assert compare_structures(correct_structure, run_config.data), "The structure of the test JSON file does not match the reference structure."

# To run the test, use the following command in your terminal:
# pytest test_json_structure.py
