import pandas as pd
import sys
import os
sys.path.append("../samplesheet_check")
from samplesheet_api import Samplesheet

class Subsetter:
    '''
    This class represents the set of action that creates 
    the subset of data that will be processed on this run. 
    In doing so, it will also update the samplesheet
    '''

    def __init__(self, input_file):
        samplesheet = Samplesheet(input_file) 
        self.samplesheet = samplesheet
        self.dataframe = pd.DataFrame(samplesheet.data)

    def create_batch(self, target_size=0.8):
        '''
        This function will take the files that needs to be processed
        and create a list of maximum the size.
        Files will be appended until the target size is reached, or the list
        of "to-be-processed" files is ended.
        Every time a file is added to the batch, its basecalled status
        changes to 'in progress'. This update will be processed to the
        json file only if everything went right 

        It will return a list of dict. 
        '''
        all_non_basecalled_files = self.dataframe[self.dataframe['basecalled'] == False]
        cumulative_size = 0
        batch = []

        for i, row in all_non_basecalled_files.iterrows():
            file_size = row['size(GB)']
            #Check
            if self._check_file_exist(row):
                #Add
                batch.append(row.to_dict())
                #Update
                self.dataframe.loc[i, 'basecalled'] = 'In progress'
                cumulative_size += file_size
            else: 
                # Here we can modify the handling of this situation
                print('WARNING: error in locating the files')
                sys.exit(1) 
            if cumulative_size >= target_size: 
                break

        #Update the samplesheet file (every file was verified)
        self.samplesheet.data = self.dataframe.to_dict(orient='records')
        self.samplesheet.update_json_file()

        return batch
    
    def _check_file_exist(self, samplesheet_entry):
        '''
        Check if the file actually exist
        '''
        path = samplesheet_entry['path']
        if os.path.exists(path):
            print("File %s exists." % samplesheet_entry['name'])
            return True
        else:
            print("File %s does not exist in %s " % (samplesheet_entry['name'], path))
            return False
