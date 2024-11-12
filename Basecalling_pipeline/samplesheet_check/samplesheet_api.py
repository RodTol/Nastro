#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"

import json
import sys 
import time
import os

class Samplesheet:
    '''
    Class used to represent and interact with the samplesheet 
    of the experiment. The json file needs to already exist
    '''

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.read_file()
    
    def read_file(self, retries=3, delay=2):
        '''
        Given a path to the samplesheet.json file, return it as data. Check if 
        all the parameters are correct also. THIS DOES NOT UPDATE self.data.
        Retries in case of JSON decoding errors.
        '''
        attempt = 0
        while attempt < retries:
            try:
                with open(self.file_path, 'r') as file:
                    data = json.load(file)
                # Verify the samplesheet data
                if self._verify_samplesheet(data):
                    return data
                else:
                    print("Samplesheet verification failed. See above for details.")
                    sys.exit(1)
            except FileNotFoundError:  # Does it exist?
                print(f"File not found: {self.file_path}")
                sys.exit(1)
            except json.JSONDecodeError:  # Is it a JSON file?
                attempt += 1
                print(f"Error decoding JSON from file: {self.file_path}. Retrying (attempt #{attempt}) in {delay} seconds...")
                time.sleep(delay)
        print("Failed to read valid JSON data after multiple attempts.")
        sys.exit(1)

    def _verify_samplesheet(self, json_data):
        '''
        Given the loaded json file, run a check to see if the file is correct
        '''
        if "metadata" not in json_data or "files" not in json_data:
            print("The JSON file must contain 'metadata' and 'files' sections.")
            return False
        
        if self._verify_metadata(json_data["metadata"]) and self._verify_files(json_data["files"]):
            #print("All elements in the list have the required parameters.")
            return True
        else:
            print("Not all elements have the required parameters.")
            return False

    def _verify_files(self, elements):
            '''
            This function will check if all the elements have the same 4 
            keys. Note that I do not check the values for any of the keys
            '''
            required_keys = {"name", "path", "size(GB)", "basecalled", "aligned", "run_id"}

            # Check if elements is a list
            if not isinstance(elements, list):
                print(f"Expected a list of dictionaries, got {type(elements).__name__}.")
                return False

            # Iterate over the list to ensure each element is a dictionary with the required keys
            for element in elements:
                if not isinstance(element, dict):
                    print(f"Expected a dictionary, got {type(element).__name__}.")
                    return False
                if not required_keys.issubset(element.keys()):
                    print(f"{element} does not have the required parameters.")
                    return False
            return True

    def _verify_metadata(self, metadata):
        '''
        Verify the metadata section
        '''
        required_keys = {"dir", "model", "outputLocation"}
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
        self.data = self.read_file()
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
        self.data = self.read_file()
        return self.data.get("files", [])

    def add_file(self, file_entry):
        '''
        Add a new file entry to the files list
        '''
        if self._verify_files([file_entry]):
            self.data["files"].append(file_entry)
            return True
        else:
            print("I wasn't able to append the entry.")
            return False


    def file_belongs_to_samplesheet(self, file_path,):
        for file in self.data["files"]:
            if  file["path"] == file_path:
                #print(f"{file_path} found")
                return True
        return False


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

    def  get_run_id(self, name):
        self.data = self.read_file()            
        for entry in self.data["files"]:
            if entry["name"] == name:
                return entry["run_id"]
        print(f"I wasn't able to find {name}")
        return False      
    
    def summary_runs(self):
        self.data = self.read_file()
        runs_id = []
        for entry in self.data["files"]:
            if entry["run_id"] not in runs_id:
                if entry["run_id"] == "":
                    runs_id.append("To be assigned")
                else:
                    runs_id.append(entry["run_id"])                

        # Create a list to store our table rows
        table = []
        
        # Add header row
        table.append(f"{'Run ID':<10} {'Basecalled':<20} {'Aligned':<20}")
        table.append("-" * 50)  # Separator line

        for run in runs_id:
            status = self.status_run(run)
            file_to_do = status[0]
            file_basecalled = status[2]
            file_aligned = status[3]
            
            # Add a row for each run
            table.append(f"{run:<10} {file_basecalled}/{file_to_do:<20} {file_aligned}/{file_to_do:<20}")

        # Join all rows into a single string
        return "\n".join(table)

    def status_run(self, run_id):
        self.data = self.read_file()
        file_to_do = 0
        file_done = 0
        file_basecalled = 0
        file_aligned = 0
        
        for entry in self.data["files"]:
            if entry["run_id"] == run_id:
                file_to_do += 1  # Count all files for this run
                if entry["basecalled"] and entry["aligned"]:
                    file_done += 1  # Fully processed files
                elif entry["basecalled"] and not entry["aligned"]:
                    file_basecalled += 1  # Basecalled but not aligned
                elif not entry["basecalled"] and not entry["aligned"]:
                    file_aligned += 1  # Neither basecalled nor aligned
                elif entry.get("basecalled") == "Failed" or entry.get("Failed") == "True":
                    file_basecalled = "X"  # Mark failure
                    file_aligned = "X"  # Mark failure
                    return [file_to_do, file_done, file_basecalled, file_aligned]

        return [file_to_do, file_done, file_basecalled, file_aligned]
    
    def list_files(self):
        self.data = self.read_file()
        files = []
        for entry in self.data["files"]:
            files.append(entry["name"])
        
        sorted_filenames = sorted(files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        return sorted_filenames

def create_samplesheet_entry(file_path):
    '''
    Create a dictionary entry for a samplesheet from a given file path.
    '''
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024**3) 

        entry = {
            "name": file_name,
            "path": file_path,
            "size(GB)": round(file_size, 2),  # Round to 2 decimal places
            "basecalled": False,  
            "aligned": False,
            "run_id": ""
        }

        return entry

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while creating samplesheet entry: {e}")
        return None

if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python samplesheet_api.py <path_to_samplesheet.json>")
        sys.exit(1)

    file_path = sys.argv[1]
    samplesheet = Samplesheet(file_path)
    print(samplesheet.summary_runs())