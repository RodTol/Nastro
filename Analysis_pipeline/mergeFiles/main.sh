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

#SBATCH --job-name=mergeFiles
#SBATCH --time=02:00:00
#SBATCH --output=merge.out
#SBATCH --error=merge.err
#SBATCH -A lage
#SBATCH -p EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60GB

# Function to check for specific files in a directory
check_ResultsFiles_in_directory() {
    local dir_path="$1"
    local basecalling_file="BasecallingResults.fastq"
    local alignment_file="AlignmentResults.bam"

    # List all files in the directory
    files_in_dir=$(ls "$dir_path")

    # Check for the presence of basecalling and alignment files
    if [[ "$files_in_dir" == *"$basecalling_file"* ]] && [[ "$files_in_dir" == *"$alignment_file"* ]]; then
        return 0  # Both files exist
    else
        return 1  # One or both files are missing
    fi
}

send_telegram_message() {
    local MESSAGE="$1"
    
    # Encode newline characters
    local PARSED_MESSAGE=$(echo "$MESSAGE" | sed ':a;N;$!ba;s/\n/%0A/g')

    # Send the message via Telegram API
    curl -s -X POST "https://api.telegram.org/bot$BC_TOKEN_BOT/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$PARSED_MESSAGE" \
        -d "parse_mode=Markdown"
}

# Get samplesheet path and id from arguments
samplesheet_path="$1"
id="$2"

module load samtools
source ~/.bashrc
conda activate fastcat

send_telegram_message "-----ANALYSIS-RUN----- 
Started analysis run for $id"
echo ""

# Assuming you have a command line tool or another way to extract metadata from the samplesheet
output_dir=$(jq -r '.metadata.outputLocation' "$samplesheet_path")

pathToFinalBasecalling="$output_dir/BasecallingResults.fastq"
pathToFinalAlignment="$output_dir/AlignmentResults.bam"

# Check if the result files already exist in the directory
if check_ResultsFiles_in_directory "$output_dir"; then
    echo "Results file are already present!"

    #Remove fastcat histograms
    rm -rf $output_dir/histograms

    # Concatenate fastq files
    cat_command="fastcat --histograms=$output_dir/histograms $output_dir/output/$id/run_${id}_merged.fastq $pathToFinalBasecalling > $output_dir/tmp.fastq"
    samtools_command="samtools merge -f -o $output_dir/tmp.bam $pathToFinalAlignment $output_dir/output/$id/run_${id}.bam"

    # Execute the cat command
    if eval "$cat_command"; then
        echo "Successfully concatenated fastq files"
        #Rename
        #rsync -a --info=progress2 --remove-source-files $output_dir/tmp.fastq $pathToFinalBasecalling
        mv $output_dir/tmp.fastq $pathToFinalBasecalling
    else
        echo "Error concatenating fastq files"
        exit 1
    fi

    # Execute the samtools merge command
    if eval "$samtools_command"; then
        echo "Successfully merged BAM files"
        #Rename
        #rsync -a --info=progress2 --remove-source-files $output_dir/tmp.bam $pathToFinalAlignment
        mv $output_dir/tmp.bam $pathToFinalAlignment
    else
        echo "Error merging BAM files"
        exit 1
    fi

    send_telegram_message "File already present. I successfully merged the files for $id"

else
    echo "First time creating Results file"

    # Move the initial .fastq and .bam files to final locations
    cp "$output_dir/output/$id/run_${id}_merged.fastq" "$pathToFinalBasecalling"
    cp "$output_dir/output/$id/run_${id}.bam" "$pathToFinalAlignment"

    send_telegram_message "No file was present. I successfully copied the files for $id"

fi
