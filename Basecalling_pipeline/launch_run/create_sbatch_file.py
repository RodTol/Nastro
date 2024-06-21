import sys
import json

# Function to load JSON data from a file
def load_json(path):
    with open(path, 'r') as file:
        data = json.load(file)
        return data

def check_json_structure(path):
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

    data = load_json(path)
    # Check the structure
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

    # Check the structure of the loaded JSON against the expected structure
    if check_structure(expected_structure, data):
        print("JSON structure is correct")
        return True
    else:
        print("JSON structure is incorrect")
        return False 

def create_sbatch_file(config):
    '''
    Function to create a Slurm sbatch script based on a configuration
    file (config.json). See the documentation to understand what each 
    parameter represents
    '''
    # Get the number of nodes that will be used for the basecalling
    how_many_nodes = len(config['Resources']['nodes_list'])

    # Open the sbatch file for writing
    with open("script_resources.sh", "w") as sbatch_file:
        # Write the basic sbatch directives
        sbatch_file.write('#!/bin/bash\n')
        sbatch_file.write(f"#SBATCH --job-name={config['General']['run_name']}\n")
        sbatch_file.write(f"#SBATCH --time={config['General']['run_time']}\n")
        sbatch_file.write(f"#SBATCH --output={config['Slurm']['output']}\n")
        sbatch_file.write(f"#SBATCH --error={config['Slurm']['error']}\n")
        
        sbatch_file.write("\n")

        # Loop through each node and write its directives
        for i in range(how_many_nodes):
            sbatch_file.write(f"#SBATCH -A lage -p {config['Resources']['nodes_queue'][i]}")
            # If a specific node is not specified let slurm decide
            if config['Resources']['nodes_list'][i] != "":
                sbatch_file.write(f" --nodelist={config['Resources']['nodes_list'][i]}")
            
            sbatch_file.write(f" --nodes=1 --ntasks-per-node=1")
            sbatch_file.write(f" --cpus-per-task={config['Resources']['nodes_cpus'][i]}")
            sbatch_file.write(f" --mem={config['Resources']['nodes_mem'][i]}")

            if config['Resources']['nodes_gpus'][i] != "None":
                sbatch_file.write(f" --gpus {config['Resources']['nodes_gpus'][i]}\n")
            else:
                sbatch_file.write("\n")

            # Add a hetjob directive after each node except the last one
            if i != how_many_nodes-1:
                sbatch_file.write("#SBATCH hetjob\n\n")
            else:
                sbatch_file.write("\n")

        sbatch_file.write("\n")
        
        # Write additional sbatch directives for script execution
        sbatch_file.write('json_file=$1\n')
        sbatch_file.write("index_host=$(jq -r '.Resources.index_host' ")
        sbatch_file.write('"$json_file")\n')
        sbatch_file.write("echo 'INDEX_HOST' $index_host\n")

        sbatch_file.write("\n")

        # Loop through each node and write srun commands
        for i in range(how_many_nodes):
            # If I have only one node I do not need to use het-group
            if how_many_nodes == 1:
                sbatch_file.write(f"srun ")
            else:
                sbatch_file.write(f"srun --het-group={i} ")

            sbatch_file.write(f"{config['Slurm']['instructions']} $json_file $((index_host + {i})) &\n")

            # Add a sleep command after each srun command except the last one
            if i != how_many_nodes-1:
                sbatch_file.write("sleep 10\n")
            else:
                sbatch_file.write("wait\n")

        # Add a comment indicating the script was generated by configuration.py
        sbatch_file.write('#**********WRITTEN BY CONFIGURATION.PY**********\n')