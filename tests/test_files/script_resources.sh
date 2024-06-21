#!/bin/bash
#SBATCH --job-name=run_Provaaa
#SBATCH --time=3:00:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err

#SBATCH -A lage -p DGX --nodelist=dgx002 --nodes=1 --ntasks-per-node=1 --cpus-per-task=64 --mem=200GB --gpus 8
#SBATCH hetjob
#SBATCH -A lage -p DGX --nodelist=dgx001 --nodes=1 --ntasks-per-node=1 --cpus-per-task=64 --mem=200GB --gpus 8


json_file=$1
index_host=$(jq -r '.Resources.index_host' "$json_file")
echo 'INDEX_HOST' $index_host

srun --het-group=0 /u/area/jenkins_onpexp/BC-pipelines/BC_scripts/instructions.sh  $json_file $((index_host + 0)) &
sleep 10
srun --het-group=1 /u/area/jenkins_onpexp/BC-pipelines/BC_scripts/instructions.sh  $json_file $((index_host + 1)) &
wait
#**********WRITTEN BY CONFIGURATION.PY**********
