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

#SBATCH --job-name=ALReport
#SBATCH --time=3:0:0
#SBATCH --partition=EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=60GB
#SBATCH --output=al_report_%j.out
#SBATCH --error=al_report_%j.err 

#TODO env variables are forced
send_files() {
  local file_path="$1"
  local caption="${2:-}"
  if [[ -z "$caption" ]]; then
    curl -s -X POST "https://api.telegram.org/bot$BC_TOKEN_BOT/sendDocument" \
      -F "chat_id=$CHAT_ID" \
      -F "document=@$file_path"
  else
    curl -s -X POST "https://api.telegram.org/bot$BC_TOKEN_BOT/sendDocument" \
      -F "chat_id=$CHAT_ID" \
      -F "document=@$file_path" \
      -F "caption=$caption"
  fi
}

samplesheet=$1
id="$2"
output_dir=$(jq -r '.metadata.outputLocation' "$samplesheet")

source ~/.bashrc
conda activate pycoQC
module load samtools

cd $output_dir

#Sort the alignment file
#TODO hardcoded. Make it dependable on the env variable for the number of process
samtools sort --threads 24 -o SortedAlignmentResults.bam AlignmentResults.bam 

#Create the report 
pycoQC -f sequencing_summary.txt -a SortedAlignmentResults.bam-o report_alignment.html

echo "Alignment report creation is completed"

current_time=$(date +"%Y-%m-%d %H:%M:%S")
alignment_report="${output_dir}/report_alignment.html"

# Send the report
send_files "$alignment_report" "Alignment report generated at $current_time, for run $id"
send_telegram_message "---- run $id FINISHED ----"
