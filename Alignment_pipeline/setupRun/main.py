import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.runParameters import runParameters
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet

def create_dir(path):
    try: 
        os.makedirs(path, exist_ok = True) 
        #print("Directory '%s' created successfully" % path) 
    except OSError as error: 
        print("Directory '%s' can not be created" % path)

if __name__ == "__main__":
    samplesheet = Samplesheet(sys.argv[1])
    run_params = runParameters.from_file(sys.argv[2])

    bam_output_dir = os.path.join(run_params.output_dir, "bam")
    create_dir(bam_output_dir)

    #Get merged file and its size
    merged_file = sys.argv[3]
    size = os.path.getsize(merged_file)

    #Create sbatch file for the run in the logs dir






