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
#SBATCH --output=basecall_report.out
#SBATCH --error=basecall_report.err 

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

send_telegram_message() {
    local MESSAGE="$1"
    
    # Encode newline characters
    local PARSED_MESSAGE=$(echo "$MESSAGE" | sed ':a;N;$!ba;s/\n/%0A/g')

    # Send the message via Telegram API
    curl -s -X POST "https://api.telegram.org/bot$BC_TOKEN_BOT/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$PARSED_MESSAGE" \
        -d "parse_mode=Markdown"
}

#Start resource profiling
python3 ${HOME}/Nastro/GPU_log/resource_profiling.py $SLURM_MEM_PER_NODE $SLURM_CPUS_ON_NODE /orfeo/cephfs/home/area/jenkins_onpexp/Nastro.csv BCREP &
profiling_pid=$!

samplesheet=$1
id="$2"
output_dir=$(jq -r '.metadata.outputLocation' "$samplesheet")

source ~/.bashrc
conda activate toulligqc

send_telegram_message "ANALYSIS - Basecall-report is generating for run $id"

cd $output_dir

#Remove old report to avoid errors
rm -f report_basecalling.html

toulligqc --report-name after_run_$id \
          --telemetry-source $output_dir/sequencing_telemetry.js \
          --sequencing-summary-source $output_dir/sequencing_summary.txt \
          --html-report-path report_basecalling.html

echo "Basecalling report creation is completed"

current_time=$(date +"%Y-%m-%d %H:%M:%S")
basecalling_report="${output_dir}/report_basecalling.html"

# Send the reports
send_files "$basecalling_report" "Basecalling report generated at $current_time, for run $id"

kill $profiling_pid