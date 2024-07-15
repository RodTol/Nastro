import json
import sys 

class Samplesheet:
    '''
    Class used to represent and interact with the samplesheet 
    of the experiment
    '''

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.read_file()
    
    def read_file(self):
        '''
        Given a path to the samplesheet.json file, return it as data. Check if 
        all the parameters are correct also. THIS DOES NOT UPDATE self.data
        '''
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError: #Does it exist ?
            print(f"File not found: {self.file_path}") 
            sys.exit(1)
        except json.JSONDecodeError: #Is it a json ?
            print(f"Error decoding JSON from file: {self.file_path}")
            sys.exit(1)

        if self._verify_file(data):
            return data
        else:
            print("Something went wrong. See above for the exception")
            sys.exit(1)

    def _verify_file(self, json_data):
        '''
        Given the loaded json file, run a check to see if the file is
        correct
        '''
        if self._verify_elements(json_data):
            print("All elements in the list have the required parameters.")
            return True
        else:
            print("Not all elements have the required parameters.")
            return False

    def _verify_elements(self, elements):
            '''
            This function will check if all the elements have the same 4 
            keys. Note that I do not check the values for any of the keys
            '''
            required_keys = {"name", "path", "size(GB)", "basecalled"}
            for element in elements:
                if not required_keys.issubset(element.keys()):
                    return False
            return True
    
    def update_json_file(self):
        '''
        Update the actual JSON file with the current data object
        '''
        try:
            with open(self.file_path, 'w') as file:
                json.dump(self.data, file, indent=4)
            print("Samplesheet JSON file updated successfully.")
        except Exception as e:
            print(f"An error occurred while updating the JSON file: {e}")    

    def print_json_format(self):
        '''
        A basic print that returns the file as it is written
        '''
        print(json.dumps(self.data, indent=4))

