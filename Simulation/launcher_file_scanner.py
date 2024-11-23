import os
import sys
from time import sleep

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Basecalling_pipeline.subset_creation.pipelineInteract import Jenkins_trigger

def count_and_list_flowcells(directory):
    flowcells = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d)) and d.startswith('flowcells_')]
    return flowcells

def launch_file_scanner_run(input_path, model, output_path):
    os.makedirs(output_path, exist_ok=True)
    jenkins_parameter =  {
            "pathToDir": input_path,
            "basecallingModel" : model,
            "outputLocation": output_path,
            "performAlign": True
        }    
    
    jenkins = Jenkins_trigger()
    jenkins.start_job('tolloi/Pipeline_long_reads/FileScanner', 'akira', jenkins_parameter)

def main(input_dir, model, output_path):
    flowcells = count_and_list_flowcells(input_dir)
    print(f"Found {len(flowcells)} flowcells:")
    for flowcell in flowcells:
        print(flowcell)
        input_path = os.path.join(input_dir, flowcell)
        flowcell_output_path = os.path.join(output_path, flowcell)
        launch_file_scanner_run(input_path, model, flowcell_output_path)
        sleep(2) # to let jenkins handle the request

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python launcher_file_scanner.py <directory> <model> <output_path>")
        sys.exit(1)
    
    directory = sys.argv[1]
    model = sys.argv[2]
    output_path = sys.argv[3]
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    main(directory, model, output_path)