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

#Provided by BCProcessor
input_dir=$1
echo -e "${RED}Input directory${RESET}"
echo $input_dir

#Provided by BCProcessor
output_dir=$2
echo -e "${RED}Output path${RESET}"
echo $output_dir

#Basecalling model (i.e. dna_r10.4.1_e8.2_400bps_hac.cfg)
#Provided by BCProcessor
model=$3
echo -e "${RED}Model${RESET}"
echo $model

#Local Unix socket file 
port="$4"
echo -e "${GREEN}Port: $port ${RESET}"

#In case supervisor is not added to PATH
#supervisor_path=

#Number of clients, spawned by the supervisor
num_clients=5

ont_basecaller_supervisor --num_clients $num_clients \
--input_path $input_dir \
--save_path $output_dir \
--config $model \
--port $port 