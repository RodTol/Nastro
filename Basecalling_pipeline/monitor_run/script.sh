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

#SBATCH --job-name=Monitor
#SBATCH --time=3:0:0
#SBATCH --partition=EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=1
#SBATCH --output=monitor.out
#SBATCH --error=monitor.err

pathToSamplesheet=$1
RUN_PARAMS_PATH=$2

python3 ${HOME}/Nastro/Basecalling_pipeline/monitor_run/main.py ${RUN_PARAMS_PATH} ${pathToSamplesheet} 

# Kill the Python process
#kill $python_pid

