#!/bin/bash

if [ $# -eq 1 ] && [ -n ${1//[0-9]/} ]; then
	PERIOD=$1
	SRC_DIR=/orfeo/cephfs/scratch/area/jenkins_onpexp/experiment/HG002_src/
	DST_DIR=/orfeo/cephfs/scratch/area/jenkins_onpexp/experiment/HG002_dst/
	
	mkdir -p $SRC_DIR
	mkdir -p $DST_DIR
	
	# copy the directory structure to the destination folder 
	# (before copying the individual files)
	rsync -av -f"+ */" -f"- *" $SRC_DIR/ $DST_DIR/
	
	echo "Started sequencing at "$(date +%T)
	# parallel processes, one for each flowcell to copy the files
	# from the source to the destination folder at a uniform rate
	# based on the total number of files in each folder,
	# can vary from flowcell to flowcell
	time parallel -j 6 \
		/orfeo/cephfs/scratch/area/jenkins_onpexp/experiment/simulate_flowcell.sh ::: \
		$SRC_DIR ::: \
		$DST_DIR ::: \
		{1..6}C ::: \
		$PERIOD
	
	# in case we want to simulate all 48 flow cells
	#time parallel -j 48 $PROJECT_DIR/simulation/simulate_flowcell.sh ::: \
	#       $SRC_DIR ::: \
	#       $DST_DIR ::: \
	#       {1..6}{A..H} ::: \
	#       $PERIOD
	exit 0
else
	1>&2 echo "Error: Provided $# arguments" 
        1>&2 echo "Need 1 input argument"
        1>&2 echo "Usage: simulate_sequencing.sh simulation_duration_in_seconds"
        exit 1
fi
