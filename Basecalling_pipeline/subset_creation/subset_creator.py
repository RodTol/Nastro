#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"

import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet

class Subsetter:
    '''
    This class represents the set of action that creates 
    the subset of data that will be processed on this run. 
    In doing so, it will also update the samplesheet
    '''

    def __init__(self, input_file):
        samplesheet = Samplesheet(input_file) 
        self.samplesheet = samplesheet
        #Only the files and not the metadata

    def create_subset(self, run_id, target_size=0.8):
        '''
        This function will take the files that needs to be processed
        and create a list of maximum the size.
        Files will be appended until the target size is reached, or the list
        of "to-be-processed" files is ended.
        Every time a file is added to the subset, its basecalled status
        changes to 'in progress'. This update will be processed to the
        json file only if everything went right 

        It will return a list of dict. 
        '''
        dataframe = pd.DataFrame(self.samplesheet.get_files())
        all_non_basecalled_files = dataframe[dataframe['basecalled'] == False]
        #cast to object type beacuse I will have both booleans and strings
        all_non_basecalled_files['basecalled'] = all_non_basecalled_files['basecalled'].astype(object)

        cumulative_size = 0
        subset = []        

        if len(all_non_basecalled_files) == 0:
            print("THERE ARE NO FILE TO BE PROCESSED")
            return subset, cumulative_size

        for i, row in all_non_basecalled_files.iterrows():
            file_size = row['size(GB)']
            #Check
            if self._check_file_exist(row):
                #Add
                subset.append(row.to_dict())
                #Update 
                dataframe.loc[i, 'basecalled'] = run_id
                dataframe.loc[i, 'run_id'] = run_id
                cumulative_size += file_size
            else: 
                # Here we can modify the handling of this situation
                print('WARNING: error in locating the files')
                sys.exit(1) 
            if cumulative_size >= target_size: 
                break

        #Update the samplesheet file (every file was verified)
        self.samplesheet.data["files"] = dataframe.to_dict(orient='records')
        self.samplesheet.update_json_file()

        return subset, cumulative_size
    
    def _check_file_exist(self, samplesheet_entry):
        '''
        Check if the file for a given path actually exist
        '''
        path = samplesheet_entry['path']
        if os.path.exists(path):
            print("File %s exists." % samplesheet_entry['name'])
            return True
        else:
            print("File %s does not exist in %s " % (samplesheet_entry['name'], path))
            return False

