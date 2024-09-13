#!/bin/bash
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
output_dir=$(jq -r '.metadata.outputLocation' "$samplesheet")

source ~/python_venvs/NanoPlot_venv/bin/activate
module load java
module load samtools

cd $output_dir

mkdir basecalling_report
NanoPlot  -t 12 --huge -o $output_dir/basecalling_report --fastq_rich BasecallingResults.fastq &

mkdir alignment_report
samtools sort AlignmentResults.bam -o SortedAlignmentResults.bam
qualimap bamqc -bam SortedAlignmentResults.bam -outdir $output_dir/alignment_report -nt 12 -outformat PDF --java-mem-size=10G &

wait
echo "Report creation is completed"

current_time=$(date +"%Y-%m-%d %H:%M:%S")
send_files("${output_dir}/basecalling_report/NanoPlot-report.html", "Basecalling report at $current_time, for run $id")
send_files("${output_dir}/alignment_report/report.pdf", "Alignment report at $current_time, for run $id")