#!/bin/bash
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

source ~/python_venvs/orfeo_telegram_on_epyc/bin/activate

#python3 /u/area/jenkins_onpexp/LTS_tolloi/Orfeo_bot/main.py ${pathToSamplesheet} &
#pid=$!

deactivate

python3 ${HOME}/Pipeline_long_reads/Basecalling_pipeline/monitor_run/main.py ${RUN_PARAMS_PATH} ${pathToSamplesheet} 

# Kill the Python process
#kill $python_pid

