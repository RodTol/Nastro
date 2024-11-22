#!/bin/bash

#SRC _DIR needs to be structured as in HG002_sample_data: so 
# SRC_DIR/no_sample/*_{index}C 
#where index is a value that goes from 1 to the N flowcell sets 

# Check if 3 arguments are passed
if [ $# -eq 3 ] && [ -n "${1//[0-9]/}" ] && [ -d "$2" ] && [ -d "$3" ]; then
    PERIOD=$1
    SRC_DIR=$2
    DST_DIR=$3
    
	#Number of simulated flowcells
	FLOWCELLS=2

    # Create destination directory if it doesn't exist
    mkdir -p $DST_DIR
    
    # Copy the directory structure to the destination folder 
    # (before copying the individual files)
    rsync -av -f"+ */" -f"- *" $SRC_DIR/ $DST_DIR/
    
    echo "Started sequencing at "$(date +%T)
    
    # Parallel processes, one for each flowcell to copy the files
    # from the source to the destination folder at a uniform rate
    # based on the total number of files in each folder,
    # can vary from flowcell to flowcell
	time parallel -j 2 \
		${HOME}/Nastro/Simulation/simulate_flowcell.sh ::: \
		$SRC_DIR ::: \
		$DST_DIR ::: \
        {1..2}C ::: \  #each flowcell is called flowcell_1C, flowcell_2C, etc
		$PERIOD
    
    # Uncomment below if you want to simulate all 48 flow cells
    #time parallel -j 48 $PROJECT_DIR/simulation/simulate_flowcell.sh ::: \
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
