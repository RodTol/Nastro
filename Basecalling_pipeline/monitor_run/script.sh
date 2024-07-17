#!/bin/bash
#SBATCH --job-name=Monitor
#SBATCH --time=3:0:0
#SBATCH --partition=EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=1
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err

pathToSamplesheet=$1
RUN_PARAMS_PATH=$2

python3 /u/area/jenkins_onpexp/LTS_tolloi/Orfeo_bot/main.py ${pathToSamplesheet} &
pid=$!

python3 main.py ${RUN_PARAMS_PATH} ${pathToSamplesheet} 

# Kill the Python process
kill $python_pid

# Check if the process was successfully killed
if ps -p $python_pid > /dev/null
then
   echo "Process $python_pid could not be killed."
else
   echo "Process $python_pid has been killed successfully."
fi
