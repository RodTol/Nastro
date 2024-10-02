#!/bin/bash

#SBATCH --job-name=merge_fastcat
#SBATCH --output=merge_fastcat.log
#SBATCH --error=merge_fastcat.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=50G
#SBATCH --time=02:00:00
#SBATCH --partition=EPYC

fastq_pass_dir=$1
merged_fastq_path=$2

conda activate fastcat

echo "Starting job on $(date)"

fastcat $fastq_pass_dir > $merged_fastq_path

echo "Job finished on $(date)"

