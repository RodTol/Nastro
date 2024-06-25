#!/bin/bash
cat << "EOF"

 ____                        ___                                                     
/\  _`\   __                /\_ \    __                                              
\ \ \L\ \/\_\  _____      __\//\ \  /\_\    ___      __                              
 \ \ ,__/\/\ \/\ '__`\  /'__`\\ \ \ \/\ \ /' _ `\  /'__`\                            
  \ \ \/  \ \ \ \ \L\ \/\  __/ \_\ \_\ \ \/\ \/\ \/\  __/                            
   \ \_\   \ \_\ \ ,__/\ \____\/\____\\ \_\ \_\ \_\ \____\                           
    \/_/    \/_/\ \ \/  \/____/\/____/ \/_/\/_/\/_/\/____/                           
                 \ \_\                                                               
                  \/_/                                                               
 __                                        ____                        __            
/\ \                                      /\  _`\                     /\ \           
\ \ \        ___     ___      __          \ \ \L\ \     __     __     \_\ \    ____  
 \ \ \  __  / __`\ /' _ `\  /'_ `\  _______\ \ ,  /   /'__`\ /'__`\   /'_` \  /',__\ 
  \ \ \L\ \/\ \L\ \/\ \/\ \/\ \L\ \/\______\\ \ \\ \ /\  __//\ \L\.\_/\ \L\ \/\__, `\
   \ \____/\ \____/\ \_\ \_\ \____ \/______/ \ \_\ \_\ \____\ \__/.\_\ \___,_\/\____/
    \/___/  \/___/  \/_/\/_/\/___L\ \         \/_/\/ /\/____/\/__/\/_/\/__,_ /\/___/ 
                              /\____/                                                
                              \_/__/                                                 
------------------------------------------------------------------------------------
EOF

# Color for bash echo
RED="\033[0;31m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
RESET="\033[0m"

# Input parameters are the config.json and what node I am on the list 
json_file=$1
my_index=$2

# Read from config.json file (necessary)
model=$(jq -r '.Basecalling.model' "$json_file")
input_dir=$(jq -r '.Basecalling.input_dir' "$json_file")
output_dir=$(jq -r '.Basecalling.output_dir' "$json_file") 
logs_dir=$(jq -r '.Basecalling.logs_dir' "$json_file")


host_index=$(jq -r '.ComputingResources.index_host' "$json_file")
port=$(jq -r '.ComputingResources.port' "$json_file")
node_queue=$(jq -r --argjson my_index "$my_index" '.ComputingResources.nodes_queue[$my_index]' "$json_file")
node_name=$(jq -r --argjson my_index "$my_index" '.ComputingResources.nodes_list[$my_index]' "$json_file")
gpus_settings=$(jq -r --argjson my_index "$my_index" '.ComputingResources.gpus[$my_index]' "$json_file")

echo -e "${RED}I am this node_name: $node_name${RESET}, and for Slurm: $SLURM_NODELIST"

# Update config.json file
if  [ "$node_name" == "" ]; then
  echo -e "${CYAN}||| Update node_name from ${RESET} $node_name ${CYAN} to ${RESET} $SLURM_NODELIST ${CYAN} |||${RESET}"
  node_name=$SLURM_NODELIST
fi
# Brief output for checking everything it's correct
echo -e "${RED}Cuda visible devices:${RESET} $CUDA_VISIBLE_DEVICES" 
echo -e "${RED}GPUs selected: $gpus_settings${RESET}"
echo -e "${RED}-----------------------${RESET}"
echo "Model: $model"
echo "Node queue: $node_queue"
echo "Logs Directory: $logs_dir"
echo "Input Directory: $input_dir"
echo "Output Directory: $output_dir"
echo -e "${RED}-----------------------${RESET}"

#Load virtualenv
#TODO: hardcoded path to virtualenv
if [ "$node_queue" == "DGX" ]; then
  source /u/area/jenkins_onpexp/python_venvs/DGX_dorado_venv/bin/activate
  echo -e "${CYAN}$node_name is loading DGX venv, given ${node_queue}${RESET}"
elif [ "$node_queue" == "GPU" ]; then
  source /u/area/jenkins_onpexp/python_venvs/GPU_dorado_venv/bin/activate
  echo -e "${CYAN}$node_name is loading GPU venv, given ${node_queue}${RESET}"
else
  echo -e "${RED}SOMETHING WRONG IN THE VIRTUALENV FOR BC SOFTWARE${RESET}"
fi

# Each node has its own dir with the port file for the connection
# and the logs from the server
mkdir $logs_dir/server_node_$node_name
cd $logs_dir/server_node_$node_name

echo -e "${RED}$(date +"%Y-%m-%d %H:%M:%S") Launching the server ${RESET}"
${HOME}/Pipeline_long_reads/Basecalling_pipeline/launch_run/server.sh $model $logs_dir/server_node_$node_name $gpus_settings $port &

while true; do
    port_file=$(grep "Starting server on port:" $logs_dir/Run_* | sed 's/.*Starting server on port: //')
    # Handle empty response
    if [ -z "$port_file" ]; then
        port_file="Port file not found"
    fi
    echo $port_file
    output=$(python3 ${HOME}/Pipeline_long_reads/Basecalling_pipeline/launch_run/check_icp_port.py ${port_file})
    if [[ "$output" == *"True"* ]]; then
        echo "Connection is up!"
        break
    else
        #echo "Connection is down."
        sleep 1
    fi
done

echo -e "${RED}$(date +"%Y-%m-%d %H:%M:%S") Server is up and running. ${RESET}"

# Start BCManager and BCController on host node
if ((my_index == host_index)); then
  BC_manager_log_path=${logs_dir}/BCManager_log.txt
  python3 ${HOME}/Pipeline_long_reads/Basecalling_pipeline/launch_run/BC_software/BCManagement.py $json_file $my_index >> "$BC_manager_log_path" 2>&1 &

  sleep 5
  
  BC_controller_log_path=${logs_dir}/BCController_log_$node_name.txt
  python3 ${HOME}/Pipeline_long_reads/Basecalling_pipeline/launch_run/BC_software/BCController.py $json_file $my_index >> "$BC_controller_log_path" 2>&1 &
  
  sleep 5
fi

# Start BCProcessor
BC_processor_log_path="${logs_dir}/BCProcessor_log_$node_name.txt"
python3 ${HOME}/Pipeline_long_reads/Basecalling_pipeline/launch_run/BC_software/BCProcessors.py $json_file $my_index >> $BC_processor_log_path 2>&1 

wait

wait