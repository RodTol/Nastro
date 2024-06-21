import json
import sys
from typing import List, Dict


class General:
    '''
    Class containing the general info about the run. It 
    needs a ConfigFile object, whose data field will be 
    immediatly updated
    '''
    def __init__(self, config_file, name: str, run_time: str):
        self.config = config_file
        self._name = name
        self._run_time = run_time

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.config.data['General']['name'] = value

    @property
    def run_time(self):
        return self._run_time

    @run_time.setter
    def run_time(self, value):
        self._run_time = value
        self.config.data['General']['run_time'] = value

    def to_dict(self):
        '''
        Returna dict without the config object field of 
        the class
        '''
        return {
            'name': self._name,
            'run_time': self._run_time
        }        

class Slurm:
    '''
    Class containing the slurm options for the run. It 
    needs a ConfigFile object, whose data field will be 
    immediatly updated
    '''
    def __init__(self, config_file, output_path: str, error_path: str, main_script: str):
        self.config = config_file
        self._output_path = output_path
        self._error_path = error_path
        self._main_script = main_script

    @property
    def output_path(self):
        return self._output_path

    @output_path.setter
    def output_path(self, value):
        self._output_path = value
        self.config.data['Slurm']['output_path'] = value

    @property
    def error_path(self):
        return self._error_path

    @error_path.setter
    def error_path(self, value):
        self._error_path = value
        self.config.data['Slurm']['error_path'] = value

    @property
    def main_script(self):
        return self._main_script

    @main_script.setter
    def main_script(self, value):
        self._main_script = value
        self.config.data['Slurm']['main_script'] = value

    def to_dict(self):
        '''
        Returna dict without the config object field of 
        the class
        '''
        return {
        "output_path":  self._output_path ,
        "error_path":   self._error_path,
        "main_script":  self._main_script
        }          

class Basecalling:
    '''
    Class containing the basecalling options for the run. It 
    needs a ConfigFile object, whose data field will be 
    immediatly updated
    '''
    def __init__(self, config, model: str, input_dir: str, output_dir: str, logs_dir: str, supervisor_script_path: str):
        self.config = config
        self._model = model
        self._input_dir = input_dir
        self._output_dir = output_dir
        self._logs_dir = logs_dir
        self._supervisor_script_path = supervisor_script_path

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value
        self.config.data['Basecalling']['model'] = value

    @property
    def input_dir(self):
        return self._input_dir

    @input_dir.setter
    def input_dir(self, value):
        self._input_dir = value
        self.config.data['Basecalling']['input_dir'] = value

    @property
    def output_dir(self):
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value):
        self._output_dir = value
        self.config.data['Basecalling']['output_dir'] = value

    @property
    def logs_dir(self):
        return self._logs_dir

    @logs_dir.setter
    def logs_dir(self, value):
        self._logs_dir = value
        self.config.data['Basecalling']['logs_dir'] = value

    @property
    def supervisor_script_path(self):
        return self._supervisor_script_path

    @supervisor_script_path.setter
    def supervisor_script_path(self, value):
        self._supervisor_script_path = value
        self.config.data['Basecalling']['supervisor_script_path'] = value

    def to_dict(self):
        '''
        Returna dict without the config object field of 
        the class
        '''
        return {
            "model": self._model,
            "input_dir": self._input_dir,
            "output_dir": self._output_dir,
            "logs_dir": self._logs_dir,
            "supervisor_script_path": self._supervisor_script_path
        }            

class ComputingResources:
    '''
    Class containing the set of resources to be requested for the run.  It 
    needs a ConfigFile object, whose data field will be 
    immediatly updated
    '''
    def __init__(self, config, index_host: str, nodes_queue: List[str], nodes_list: List[str], nodes_ip: List[str], 
                 nodes_cpus: List[str], nodes_mem: List[str], nodes_gpus: List[str], gpus: List[str], 
                 batch_size_list: List[str]):
        self.config = config
        self._index_host = index_host
        self._nodes_queue = nodes_queue
        self._nodes_list = nodes_list
        self._nodes_ip = nodes_ip
        self._nodes_cpus = nodes_cpus
        self._nodes_mem = nodes_mem
        self._nodes_gpus = nodes_gpus
        self._gpus = gpus
        self._batch_size_list = batch_size_list

    @property
    def index_host(self):
        return self._index_host

    @index_host.setter
    def index_host(self, value):
        self._index_host = value
        self.config.data['index_host'] = value

    @property
    def nodes_queue(self):
        return self._nodes_queue

    @nodes_queue.setter
    def nodes_queue(self, value):
        self._nodes_queue = value
        self.config.data['nodes_queue'] = value

    @property
    def nodes_list(self):
        return self._nodes_list

    @nodes_list.setter
    def nodes_list(self, value):
        self._nodes_list = value
        self.config.data['nodes_list'] = value

    @property
    def nodes_ip(self):
        return self._nodes_ip

    @nodes_ip.setter
    def nodes_ip(self, value):
        self._nodes_ip = value
        self.config.data['nodes_ip'] = value

    @property
    def nodes_cpus(self):
        return self._nodes_cpus

    @nodes_cpus.setter
    def nodes_cpus(self, value):
        self._nodes_cpus = value
        self.config.data['nodes_cpus'] = value

    @property
    def nodes_mem(self):
        return self._nodes_mem

    @nodes_mem.setter
    def nodes_mem(self, value):
        self._nodes_mem = value
        self.config.data['nodes_mem'] = value

    @property
    def nodes_gpus(self):
        return self._nodes_gpus

    @nodes_gpus.setter
    def nodes_gpus(self, value):
        self._nodes_gpus = value
        self.config.data['nodes_gpus'] = value

    @property
    def gpus(self):
        return self._gpus

    @gpus.setter
    def gpus(self, value):
        self._gpus = value
        self.config.data['gpus'] = value

    @property
    def batch_size_list(self):
        return self._batch_size_list

    @batch_size_list.setter
    def batch_size_list(self, value):
        self._batch_size_list = value
        self.config.data['batch_size_list'] = value

    def to_dict(self):
        '''
        Returna dict without the config object field of 
        the class
        '''
        return {
            "index_host": self._index_host,
            "nodes_queue": self._nodes_queue,
            "nodes_list": self._nodes_list,
            "nodes_ip": self._nodes_ip,
            "nodes_cpus": self._nodes_cpus,
            "nodes_mem": self._nodes_mem,
            "nodes_gpus": self._nodes_gpus,
            "gpus": self._gpus,
            "batch_size_list": self._batch_size_list
        }

class ConfigFile:
    '''
    This class represents and interact with a config file
    that sets all the options for the basecalling run.

    If the file does not exist, a new json file will be created
    with an empty dict (in order to be compliant to json format)

    Maybe do getter and setter also for him
    '''

    def __init__(self, file_path, general=None, slurm=None, basecalling=None, computing_resources=None):
        self.path_to_json = file_path
        if self.file_exists() and check_config_json_structure(file_path):
            print(f"The file '{file_path}' already exists and has the complete json structure.")
            # Load the data
            self.data = self.read_file()  
            self._general = General(self, **self.data['General'])
            self._slurm = Slurm(self, **self.data['Slurm'])
            self._basecalling = Basecalling(self, **self.data['Basecalling'])
            self._computing_resources = ComputingResources(self, **self.data['ComputingResources'])           
        else:
            print(f"The file '{file_path}' does not exist or has incomplete json structure. Creating empty file.")
            self.data = {}  # empty dict
            self._general = general
            self._slurm = slurm
            self._basecalling = basecalling
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
    def basecalling(self):
        return self._basecalling
    
    @basecalling.setter
    def basecalling(self, value):
        self._basecalling = value
        # Update with the dictionary representation of the object
        # but we need to remove the general.config
        self.data['Basecalling'] = value.to_dict()
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
        "Basecalling": {
            "model": str,
            "input_dir": str,
            "output_dir": str,
            "logs_dir": str,
            "supervisor_script_path": str,
        },
        "ComputingResources": {
            "index_host": str,
            "nodes_queue": list,
            "nodes_list": list,
            "nodes_ip": list,
            "nodes_cpus": list,
            "nodes_mem": list,
            "nodes_gpus": list,
            "gpus": list,
            "batch_size_list": list,
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