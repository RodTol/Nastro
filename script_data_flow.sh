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

#SBATCH --job-name=data_flow
#SBATCH --time=06:00:00
#SBATCH --output=/u/area/jenkins_onpexp/Nastro/data_flow/data_flow.out
#SBATCH --error=/u/area/jenkins_onpexp/Nastro/data_flow/data_flow.err
#SBATCH -A lage
#SBATCH -p EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=10GB

source=$1
dest=$2

python3 /u/area/jenkins_onpexp/BC-pipelines/simulation-pipeline/utility/data_flow_emulator.py $source $dest