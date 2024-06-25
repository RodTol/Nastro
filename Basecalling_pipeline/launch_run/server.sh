#!/bin/bash

#Color for bash echo
RED="\033[0;31m"
GREEN="\033[0;32m"
RESET="\033[0m"  

echo -e "${GREEN}-------------------------------------${RESET}"
echo -e "${GREEN}SERVER SCRIPT${RESET}"

#Basecalling model (i.e. dna_r10.4.1_e8.2_400bps_hac.cfg)
model="$1"
echo -e "${GREEN}model $model${RESET}"

#Path for the log files of the basecaller server
log_path="$2"
echo -e "${GREEN}Log files path: ${log_path} ${RESET}"

#Gpus selection (i.e. cuda:all/cuda:0,1,2)
gpus_settings="$3"
echo -e "${GREEN}GPUs selected: ${gpus_settings} ${RESET}"

#Local Unix socket file 
port="$4"
echo -e "${GREEN}Port: $port ${RESET}"

#In case dorado is not added to PATH
#dorado_server_path=

#Launching the dorado basecaller server
dorado_basecall_server \
--config $model \
--log_path $log_path \
--device $gpus_settings \
--port $port 