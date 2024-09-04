import sys 
import os
import json 


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.config_file_api import General
from Basecalling_pipeline.subset_creation.config_file_api import Slurm

class Alignment:
    def __init__(self, config, input_file: str, output_file: str, logs_dir: str, reference_genome: str, additional_flags: str):
        self.config = config
        self._input_file = input_file
        self._output_file = output_file
        self._logs_dir = logs_dir
        self._reference_genome = reference_genome
        self._additional_flags = additional_flags

    @property
    def input_file(self):
        return self._input_file

    @input_file.setter
    def input_file(self, value):
        self._input_file = value
        self.config.data['Alignment']['input_file'] = value

    @property
    def output_file(self):
        return self._output_file

    @output_file.setter
    def output_file(self, value):
        self._output_file = value
        self.config.data['Alignment']['output_file'] = value

    @property
    def logs_dir(self):
        return self._logs_dir

    @logs_dir.setter
    def logs_dir(self, value):
        self._logs_dir = value
        self.config.data['Alignment']['logs_dir'] = value

    @property
    def reference_genome(self):
        return self._reference_genome

    @reference_genome.setter
    def reference_genome(self, value):
        self._reference_genome = value
        self.config.data['Alignment']['reference_genome'] = value        

    @property
    def additional_flags(self):
        return self._additional_flags

    @additional_flags.setter
    def additional_flags(self, value):
        self._additional_flags = value
        self.config.data['Alignment']['additional_flags'] = value

    def to_dict(self):
        '''
        Returna dict without the config object field of 
        the class
        '''
        return {
            "input_file": self._input_file,
            "output_file": self._output_file,
            "logs_dir": self._logs_dir,
            "reference_genome": self._reference_genome,
            "additional_flags": self._additional_flags
        }                
    
class ComputingResources:
    def __init__(self, config, node_queue: str, node_name: str, 
                 node_cpus: str, node_mem: str):
        self.config = config
        self._node_queue = node_queue
        self._node_name = node_name
        self._node_cpus = node_cpus
        self._node_mem = node_mem
 
    @property
    def node_queue(self):
        return self._nodes_queue

    @node_queue.setter
    def node_queue(self, value):
        self._nodes_queue = value
        self.config.data['node_queue'] = value

    @property
    def node_name(self):
        return self._node_name

    @node_name.setter
    def node_name(self, value):
        self._node_name = value
        self.config.data['node_name'] = value

    @property
    def node_cpus(self):
        return self._node_cpus

    @node_cpus.setter
    def node_cpus(self, value):
        self._node_cpus = value
        self.config.data['node_cpus'] = value

    @property
    def node_mem(self):
        return self._node_mem

    @node_mem.setter
    def node_mem(self, value):
        self._node_mem = value
        self.config.data['nodes_mem'] = value

    def to_dict(self):
        '''
        Returna dict without the config object field of 
        the class
        '''
        return {
            "node_queue": self._node_queue,
            "node_name": self._node_name,
            "node_cpus": self._node_cpus,
            "node_mem": self._node_mem
        }    
    
class AlConfigFile:
    def __init__(self, file_path, general=None, slurm=None, alignment=None, computing_resources=None):
        self.path_to_json = file_path
        if self.file_exists() and check_config_json_structure(file_path):
            print(f"The file '{file_path}' already exists and has the complete json structure.")
            # Load the data
            self.data = self.read_file()  
            self._general = General(self, **self.data['General'])
            self._slurm = Slurm(self, **self.data['Slurm'])
            self._alignment = Alignment(self, **self.data['Alignment'])
            self._computing_resources = ComputingResources(self, **self.data['ComputingResources'])           
        else:
            print(f" Creating empty file: '{file_path}' does not exist or has incomplete json structure.")
            self.data = {}  # empty dict
            self._general = general
            self._slurm = slurm
            self._alignment = alignment
            self._computing_resources = computing_resources
            self.update_json_file()  # synchronize

    @property
    def general(self):
        return self._general
    
    @general.setter
    def general(self, value):
        self._general = value
        # Update with the dictionary representation of the object
        # but we need to remove the general.config
        self.data['General'] = value.to_dict()
        self.update_json_file() #synchronize

    @property
    def slurm(self):
        return self._slurm
    
    @slurm.setter
    def slurm(self, value):
        self._slurm = value
        # Update with the dictionary representation of the object
        # but we need to remove the general.config
        self.data['Slurm'] = value.to_dict()
        self.update_json_file() #synchronize      

    @property
    def alignment(self):
        return self._alignment
    
    @alignment.setter
    def alignment(self, value):
        self._alignment = value
        # Update with the dictionary representation of the object
        # but we need to remove the general.config
        self.data['Alignment'] = value.to_dict()
        self.update_json_file() #synchronize       

    @property
    def computing_resources(self):
        return self._computing_resources
    
    @computing_resources.setter
    def computing_resources(self, value):
        self._computing_resources = value
        # Update with the dictionary representation of the object
        # but we need to remove the general.config
        self.data['ComputingResources'] = value.to_dict()
        self.update_json_file() #synchronize                  

    def file_exists(self):
        try:
            with open(self.path_to_json, 'r'):
                return True
        except FileNotFoundError:
            return False

    def read_file(self):
        '''
        Given a path to the samplesheet.json file, save it as data.
        '''
        try:
            with open(self.path_to_json, 'r') as file:
                data = json.load(file)
        except FileNotFoundError: #Does it exist ?
            print(f"File not found: {self.path_to_json}") 
            sys.exit(1)
        except json.JSONDecodeError: #Is it a json ?
            print(f"Error decoding JSON from file: {self.path_to_json}")
            sys.exit(1)
        
        return data

    def update_json_file(self):
        '''
        Update the actual JSON file with the current data object
        '''
        try:
            with open(self.path_to_json, 'w') as file:
                json.dump(self.data, file, indent=4)
            print("Config JSON file updated successfully.")
        except Exception as e:
            print(f"An error occurred while updating the JSON file: {e}")    

def check_config_json_structure(path_to_json):
    '''
    This function checks if the config.json file is correct
    '''
    # Define the expected structure
    expected_structure = {
        "General": {
            "name": str,
            "run_time": str,
        },
        "Slurm": {
            "output_path": str,
            "error_path": str,
            "main_script": str,
        },
        "Alignment": {
            "input_file": str,
            "output_file": str,
            "logs_dir": str,
            "reference_genome": str,
            "additional_flags": str
        },
        "ComputingResources": {
            "node_queue": str,
            "node_name": str,
            "node_cpus": str,
            "node_mem": str
        }
    }   

    # Check the structure function
    def check_structure(expected, actual):
        if isinstance(expected, dict):
            if not isinstance(actual, dict):
                return False
            for key, value_type in expected.items():
                if key not in actual:
                    print(f"Missing key: {key}")
                    return False
                if not check_structure(value_type, actual[key]):
                    print(f"Incorrect structure for key: {key}")
                    return False
        elif isinstance(expected, type):
            if not isinstance(actual, expected):
                print(f"Incorrect type for value, expected {expected.__name__}, got {type(actual).__name__}")
                return False
        return True

    print("Testing ", path_to_json)
    # Code duplication forced because otherwise I cannot use this function
    # without a complete instance of config_file
    try:
        with open(path_to_json, 'r') as file:
            data = json.load(file)
    except FileNotFoundError: #Does it exist ?
        print(f"File not found: {path_to_json}") 
        sys.exit(1)
    except json.JSONDecodeError: #Is it a json ?
        print(f"Error decoding JSON from file: {path_to_json}")
        sys.exit(1)
    
    # Check the structure of the loaded JSON against the expected structure
    if check_structure(expected_structure, data):
        print("JSON structure is correct")
        return True
    else:
        print("JSON structure is incorrect")
        return False             