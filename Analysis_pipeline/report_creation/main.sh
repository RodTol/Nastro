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

samplesheet=$1
output_dir=$(jq -r '.metadata.outputLocation' "$samplesheet")

source ~/python_venvs/NanoPlot_venv/bin/activate
module load java

cd $output_dir

mkdir basecalling_report
NanoPlot  -t 12 --huge -o $output_dir/basecalling_report --fastq_rich BasecallingResults.fastq &

mkdir alignment_report
qualimap bamqc -bam AlignmentResults.bam -outdir $output_dir/alignment_report --java-mem-size=10G &

wait
echo "Report creation is completed"
