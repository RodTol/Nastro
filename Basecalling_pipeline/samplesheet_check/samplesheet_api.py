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

        if self._verify_samplesheet(data):
            return data
        else:
            print("Something went wrong. See above for the exception")
            sys.exit(1)

    def _verify_samplesheet(self, json_data):
        '''
        Given the loaded json file, run a check to see if the file is correct
        '''
        if "metadata" not in json_data or "files" not in json_data:
            print("The JSON file must contain 'metadata' and 'files' sections.")
            return False
        
        if self._verify_metadata(json_data["metadata"]) and self._verify_files(json_data["files"]):
            print("All elements in the list have the required parameters.")
            return True
        else:
            print("Not all elements have the required parameters.")
            return False

    def _verify_files(self, elements):
            '''
            This function will check if all the elements have the same 4 
            keys. Note that I do not check the values for any of the keys
            '''
            required_keys = {"name", "path", "size(GB)", "basecalled", "aligned"}
            for element in elements:
                if not required_keys.issubset(element.keys()):
                    print(f"{element} does not have the required parameters.")
                    return False
            return True

    def _verify_metadata(self, metadata):
        '''
        Verify the metadata section
        '''
        required_keys = {"dir", "model"}
        if not required_keys.issubset(metadata.keys()):
            print("Wrong metadata")
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

    def get_metadata(self):
        '''
        Return the metadata section of the JSON file
        '''
        return self.data.get("metadata", {})

    def set_metadata(self, metadata):
        '''
        Set the metadata section of the JSON file
        '''
        if self._verify_metadata(metadata):
            self.data["metadata"] = metadata
        else:
            print("Invalid metadata format.")
    
    def get_files(self):
        '''
        Return the files section of the JSON file
        '''
        return self.data.get("files", [])

    def add_file(self, file_entry):
        '''
        Add a new file entry to the files list
        '''
        if self._verify_elements([file_entry]):
            self.data["files"].append(file_entry)
        else:
            print("Invalid file entry format.")

    def  check_basecalling_is_finished(self):
        self.data = self.read_file()            
        
        for entry in self.data["files"]:
            if entry["basecalled"] != "True":
                return False
        return True

    def  check_alignment_is_finished(self):
        self.data = self.read_file()            
        
        for entry in self.data["files"]:
            if entry["aligned"] != "True":
                return False
        return True

