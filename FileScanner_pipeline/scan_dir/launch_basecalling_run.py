import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.pipelineInteract import Jenkins_trigger
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet

def launch_run(samplesheet: Samplesheet):
    #Create input, logs, output dirs
    input_path = os.path.join(samplesheet.get_metadata()["outputLocation"], 'input')
    logs_path = os.path.join(samplesheet.get_metadata()["outputLocation"], 'logs')
    output_path = os.path.join(samplesheet.get_metadata()["outputLocation"], 'output')

    os.makedirs(input_path, exist_ok=True)
    os.makedirs(logs_path, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)

    jenkins_parameter =  {
            "pathToSamplesheet": samplesheet.file_path,
            "pathToInputDir" : input_path,
            "pathToOutputDir": output_path,
            "pathToLogsDir": logs_path,
            "RUN_TESTING_CLEANUP": False
        }    
    
    jenkins = Jenkins_trigger()
    jenkins.start_job('tolloi/Pipeline_long_reads/basecalling_pipeline', 'kuribo', jenkins_parameter)