#!/bin/bash

#Expected structure as in HG002_sample_data
INPUT_FOLDER=$1/*_${3}
OUTPUT_FOLDER=$2/*_${3}
RUNTIME=$4

echo "Runtime is: $RUNTIME seconds"

NUM_POD5=$(ls $INPUT_FOLDER/*.pod5 2>/dev/null | wc -l)
NUM_FAST5=$(ls $INPUT_FOLDER/*.fast5 2>/dev/null | wc -l)

echo "Found $NUM_POD5 .pod5 files and $NUM_FAST5 .fast5 files in $INPUT_FOLDER"

if [ $NUM_POD5 -gt $NUM_FAST5 ]; then
        NUM_FILES=$NUM_POD5
        FILE_EXTENSION="pod5"
else
        NUM_FILES=$NUM_FAST5
        FILE_EXTENSION="fast5"
fi

PERIOD=$(python3 -c "print (abs(int(${RUNTIME}/${NUM_FILES})))")
cd $INPUT_FOLDER

# copy one file at a time, separated by $PERIOD seconds
for i in $(ls *.${FILE_EXTENSION});
do
        cp --parents $i $OUTPUT_FOLDER/
        sleep ${PERIOD}s
done
