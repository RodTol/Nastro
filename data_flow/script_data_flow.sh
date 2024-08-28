#!/bin/bash
#SBATCH --job-name=data_flow
#SBATCH --time=06:00:00
#SBATCH --output=/u/area/jenkins_onpexp/Pipeline_long_reads/data_flow/data_flow.out
#SBATCH --error=/u/area/jenkins_onpexp/Pipeline_long_reads/data_flow/data_flow.err
#SBATCH -A lage
#SBATCH -p EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=10GB

source=/orfeo/cephfs/scratch/area/jenkins_onpexp/CliveOME
dest=$1

python3 /u/area/jenkins_onpexp/BC-pipelines/simulation-pipeline/utility/data_flow_emulator.py $source $dest