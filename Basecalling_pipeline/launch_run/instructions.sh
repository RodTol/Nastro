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
host_index=$(jq -r '.Resources.index_host' "$json_file")
node_name=$(jq -r --argjson my_index "$my_index" '.Resources.nodes_list[$my_index]' "$json_file")
model=$(jq -r '.Basecalling.model' "$json_file")
logs_dir=$(jq -r '.Basecalling.logs_dir' "$json_file")
node_queue=$(jq -r --argjson my_index "$my_index" '.Resources.nodes_queue[$my_index]' "$json_file")

input_dir=$(jq -r '.Basecalling.input_dir' "$json_file") #debug
output_dir=$(jq -r '.Basecalling.output_dir' "$json_file") #debug
gpus_settings=$(jq -r --argjson my_index "$my_index" '.Resources.gpus[$my_index]' "$json_file") #debug

echo -e "${RED}I am this node_name: $node_name${RESET}, and for Slurm: $SLURM_NODELIST"

# Update config.json file
if  [ "$node_name" == "" ]; then
  echo -e "${RED}|||Update node_name from $node_name to $SLURM_NODELIST|||${RESET}"
  node_name=$SLURM_NODELIST
fi
# Brief output for checking everything it's correct
echo $CUDA_VISIBLE_DEVICES
echo -e "${RED}GPUs selected: $gpus_settings${RESET}"
echo -e "${RED}-----------------------${RESET}"
echo "Model: $model"
echo "Node queue: $node_queue"
echo "Logs Directory: $logs_dir"
echo "Input Directory: $input_dir"
echo "Output Directory: $output_dir"
echo -e "${RED}-----------------------${RESET}"
