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

#SBATCH --job-name=Report
#SBATCH --time=3:0:0
#SBATCH --partition=EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=30GB
#SBATCH --output=repor_%j.out
#SBATCH --error=report_%j.err 

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

source ~/python_venvs/NanoPlot_venv/bin/activate
module load java
module load samtools

cd $output_dir

mkdir -p basecalling_report
NanoPlot  -t 12 --huge -o $output_dir/basecalling_report --fastq_rich BasecallingResults.fastq &

mkdir -p alignment_report
samtools sort $output_dir/AlignmentResults.bam -o $output_dir/SortedAlignmentResults.bam

#qualimap bamqc -bam SortedAlignmentResults.bam -outdir $output_dir/alignment_report -nt 12 -outformat PDF --java-mem-size=10G &
NanoPlot  -t 8 -o $output_dir/alignment_report --bam SortedAlignmentResults.bam &

wait
echo "Report creation is completed"

current_time=$(date +"%Y-%m-%d %H:%M:%S")
basecalling_report="${output_dir}/basecalling_report/NanoPlot-report.html"

#alignment_report="${output_dir}/alignment_report/report.pdf"
alignment_report="${output_dir}/alignment_report/NanoPlot-report.html"

# Send the reports
send_files "$basecalling_report" "Basecalling report generated at $current_time, for run $id"
send_files "$alignment_report" "Alignment report generated at $current_time, for run $id"
send_telegram_message "---- run $id FINISHED ----"