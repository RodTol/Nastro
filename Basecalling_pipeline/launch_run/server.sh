#!/bin/bash
#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"


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

#Collect the GPU performance data
python3 ${HOME}/Nastro/GPU_log/gpu_log_collector.py $log_path/gpu_utilization.csv &

#Modify the Orfeo bot
#JSON_FILE="/u/area/jenkins_onpexp/LTS_tolloi/Orfeo_bot/config.json" 
#jq --arg path "$SAMPLESHEET" '.SAMPLESHEET_PATH = $path' "$JSON_FILE" > tmp.$$.json && mv tmp.$$.json "$JSON_FILE"

#Launching the dorado basecaller server
dorado_basecall_server \
--config $model \
--log_path $log_path \
--device $gpus_settings \
--port $port 
#--num_dorado_worker_threads
