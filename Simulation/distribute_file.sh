#!/bin/bash

# Check for the correct number of arguments
if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <source_dir> <destination_dir> <number_of_flowcells>"
    exit 1
fi

# Input arguments
SOURCE_DIR="$1"
DESTINATION_DIR="$2"
NUM_FLOWCELLS="$3"

# Verify the source directory exists
if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "Error: Source directory '$SOURCE_DIR' does not exist."
    exit 1
fi

# Create destination directories
for i in $(seq 1 "$NUM_FLOWCELLS"); do
    mkdir -p "${DESTINATION_DIR}/flowcell_${i}C"
done

# Find .pod5 and .fast5 files and calculate total size
FILES=($(find "$SOURCE_DIR" -type f \( -name "*.pod5" -o -name "*.fast5" \)))
if [[ ${#FILES[@]} -eq 0 ]]; then
    echo "No .pod5 or .fast5 files found in '$SOURCE_DIR'."
    exit 0
fi

# Get file sizes in bytes and pair them with filenames
declare -A FILE_SIZES
for file in "${FILES[@]}"; do
    FILE_SIZES["$file"]=$(stat -c%s "$file")
done

# Sort files by size (descending)
FILES_SORTED=($(for file in "${FILES[@]}"; do
    echo "${FILE_SIZES["$file"]} $file"
done | sort -nr | awk '{print $2}'))

# Initialize flowcell size tracking
declare -A FLOWCELL_SIZES
for i in $(seq 1 "$NUM_FLOWCELLS"); do
    FLOWCELL_SIZES["flowcell_${i}C"]=0
done

# Distribute files to flowcells
for file in "${FILES_SORTED[@]}"; do
    # Find the flowcell with the smallest current size
    SMALLEST_FLOWCELL=$(for fc in "${!FLOWCELL_SIZES[@]}"; do
        echo "${FLOWCELL_SIZES[$fc]} $fc"
    done | sort -n | awk '{print $2}' | head -n1)
    
    # Copy the file to the selected flowcell
    cp "$file" "${DESTINATION_DIR}/${SMALLEST_FLOWCELL}/"
    echo "Copied '$file' to '${DESTINATION_DIR}/${SMALLEST_FLOWCELL}/'"
    
    # Update the size of the selected flowcell
    FLOWCELL_SIZES["$SMALLEST_FLOWCELL"]=$((FLOWCELL_SIZES["$SMALLEST_FLOWCELL"] + FILE_SIZES["$file"]))
done

echo "Files have been distributed to $NUM_FLOWCELLS flowcells."
