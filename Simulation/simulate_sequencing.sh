#!/bin/bash
#SBATCH --job-name=simulate_sequencing
#SBATCH --time=03:00:00
#SBATCH --output=simulate_sequencing.out
#SBATCH --error=simulate_sequencing.err
#SBATCH -A lage
#SBATCH -p EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=10GB

#SRC _DIR needs to be structured as in HG002_sample_data: so 
# SRC_DIR/no_sample/*_{index}C 
#where index is a value that goes from 1 to the N flowcell sets 

# CHECK FLOWECELLS, cpus_per_task and PARALLEL -j command
# to have same argument!!!

# Check if 3 arguments are passed
if [ $# -eq 3 ]; then
    PERIOD=$1
    SRC_DIR=$2
    DST_DIR=$3
    
    # Number of simulated flowcells
    FLOWCELLS=3

    echo "Simulation duration: $PERIOD seconds with $FLOWCELLS flowcells"

    # Create destination directory if it doesn't exist
    mkdir -p $DST_DIR
    
    # Copy the directory structure to the destination folder 
    # (before copying the individual files)
    rsync -av -f"+ */" -f"- *" $SRC_DIR/ $DST_DIR/ > /dev/null 2>&1

    echo "Started sequencing at "$(date +%T)
    
    # Parallel processes, one for each flowcell to copy the files
    # from the source to the destination folder at a uniform rate
    # based on the total number of files in each folder,
    # can vary from flowcell to flowcell
    time parallel -j 3 \
        "${HOME}/Nastro/Simulation/simulate_flowcell.sh" ::: \
        "$SRC_DIR" ::: \
        "$DST_DIR" ::: \
        {1..2}C ::: \
        "$PERIOD"

    # Uncomment below if you want to simulate all 48 flow cells
    # time parallel -j 48 $PROJECT_DIR/simulation/simulate_flowcell.sh ::: \
    #       $SRC_DIR ::: \
    #       $DST_DIR ::: \
    #       {1..6}{A..H} ::: \
    #       $PERIOD

    exit 0
else
    1>&2 echo "Error: Invalid arguments" 
    1>&2 echo "Usage: simulate_sequencing.sh simulation_duration_in_seconds SRC_directory DST_directory"
    exit 1
fi
