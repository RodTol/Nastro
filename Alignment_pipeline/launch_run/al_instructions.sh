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

#Color for bash echo
RED="\033[0;31m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
RESET="\033[0m"  

al_config=$1
id=$2
samplesheet=$3

fastq_file=$(jq -r '.Alignment.input_file' "$al_config")
bam_file=$(jq -r '.Alignment.output_file' "$al_config")
ref_genome=$(jq -r '.Alignment.reference_genome' "$al_config")
logs_dir=$(jq -r '.Alignment.logs_dir' "$al_config")

source ~/python_venvs/DGX_dorado_venv/bin/activate
dorado aligner $ref_genome $fastq_file > $bam_file

if [ $? -ne 0 ]; then
    echo "An error occurred while running the command."
    python3 ${HOME}/Nastro/Alignment_pipeline/launch_run/update_samplesheet.py $samplesheet $id "Failed" None
    exit 1
else
    echo "The command ran successfully."
    #module load samtools
    cd $logs_dir
    #samtools flagstat $bam_file > al_basic_report_${id}.txt
    module purge
    python3 ${HOME}/Nastro/Alignment_pipeline/launch_run/update_samplesheet.py $samplesheet $id "Correct" $logs_dir/al_basic_report_${id}.txt

    #echo "Launching the analysis pipeline"
    #python3 ${HOME}/Nastro/Alignment_pipeline/launch_run/launch_analysis_pipeline.py $samplesheet $id
fi


