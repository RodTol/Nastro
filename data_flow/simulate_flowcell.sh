#!/bin/bash

#Expected structure as in HG002_sample_data
INPUT_FOLDER=$1/no_sample/*_${3}
OUTPUT_FOLDER=$2/no_sample/*_${3}
RUNTIME=$4

#Compute frequency to cp .fast5 files to output dir
NUM_FAST5=$(ls $INPUT_FOLDER/ | wc -l)
PERIOD=$(python3 -c "print (abs(int(${RUNTIME}/${NUM_FAST5})))")

cd $INPUT_FOLDER

# copy one file at a time, separated by $PERIOD seconds
for i in $(ls *.fast5);
do
        cp --parents $i $OUTPUT_FOLDER/
        sleep ${PERIOD}s
done
