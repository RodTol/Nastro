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

#Color for bash echo
RED="\033[0;31m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
RESET="\033[0m"  

al_config=$1
samplesheet=$2

id=$(jq -r '.General.name' "$al_config")
fastq_file=$(jq -r '.Alignment.input_file' "$al_config")
bam_file=$(jq -r '.Alignment.output_file' "$al_config")
ref_genome=$(jq -r '.Alignment.reference_genome' "$al_config")

dorado aligner $ref_genome $fastq_file > $bam_file

if [ $? -ne 0 ]; then
    echo "An error occurred while running the command."
    python3 ${HOME}/Pipeline_long_reads/Alignment_pipeline/launch_run/update_samplesheet.py $samplesheet $id Error
    exit 1
else
    echo "The command ran successfully."
    module load samtools
    samtools flagstat $bam_file > al_basic_report_${id}.txt
    module load purge

    python3 ${HOME}/Pipeline_long_reads/Alignment_pipeline/launch_run/update_samplesheet.py $samplesheet $id True
fi


