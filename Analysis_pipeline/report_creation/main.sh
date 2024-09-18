#!/bin/bash
# Copyright 2024 Area Science Park
# Author: Rodolfo Tolloi
#
# Licensed under the Apache License, Version 2.0 (the "License");# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#SBATCH --job-name=Report
#SBATCH --time=3:0:0
#SBATCH --partition=EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=30GB
#SBATCH --output=report.out
#SBATCH --error=report.err 

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
samtools sort AlignmentResults.bam -o SortedAlignmentResults.bam
qualimap bamqc -bam SortedAlignmentResults.bam -outdir $output_dir/alignment_report -nt 12 -outformat PDF --java-mem-size=10G &

wait
echo "Report creation is completed"

current_time=$(date +"%Y-%m-%d %H:%M:%S")
basecalling_report="${output_dir}/basecalling_report/NanoPlot-report.html"
alignment_report="${output_dir}/alignment_report/report.pdf"

# Send the reports
send_files "$basecalling_report" "Basecalling report generated at $current_time, for run $id"
send_files "$alignment_report" "Alignment report generated at $current_time, for run $id"