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

#SBATCH --job-name=BASEReport
#SBATCH --time=3:0:0
#SBATCH --partition=EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=60GB
#SBATCH --output=basecall_report_%j.out
#SBATCH --error=basecall_report_%j.err 

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
conda activate toulligqc

send_telegram_message "ANALYSIS - Basecall-report is generating for run $id"

cd $output_dir

toulligqc --report-name after_run_$id \
            --telemetry-source $output_dir/sequencing_telemetry.js \
            --sequencing-summary-source $output_dir/sequencing_summary.txt \
            --html-report-path report_basecalling.html

echo "Basecalling report creation is completed"

current_time=$(date +"%Y-%m-%d %H:%M:%S")
basecalling_report="${output_dir}/report_basecalling.html"

# Send the reports
send_files "$basecalling_report" "Basecalling report generated at $current_time, for run $id"
