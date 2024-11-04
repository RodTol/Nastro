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

#SBATCH --job-name=mergeSummary
#SBATCH --time=02:00:00
#SBATCH --output=merge_sum_%j.out
#SBATCH --error=merge_sum_%j.err
#SBATCH -A lage
#SBATCH -p EPYC
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60GB

# Function to check for specific files in a directory
check_ResultsFiles_in_directory() {
    local dir_path="$1"
    local summary_file="sequencing_summary.txt"
    local telemetry_file="sequencing_telemetry.js"

    # List all files in the directory
    files_in_dir=$(ls "$dir_path")

    # Check for the presence of basecalling and alignment files
    if [[ "$files_in_dir" == *"$summary_file"* ]] && [[ "$files_in_dir" == *"$telemetry_file"* ]]; then
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

send_telegram_message "Merging the summary and telemetry files for run $id"

# Assuming you have a command line tool or another way to extract metadata from the samplesheet
output_dir=$(jq -r '.metadata.outputLocation' "$samplesheet_path")

pathToFinalSummary="$output_dir/sequencing_summary.txt"
pathToFinalTelemetry="$output_dir/sequencing_telemetry.js"

# Check if the result files already exist in the directory
if check_ResultsFiles_in_directory "$output_dir"; then
    echo "Results file are already present!"

    #Go into LOGOUTPUT directory
    cd "$output_dir/output/$id/LOGOUTPUT_"* || { echo "Directory not found"; exit 1; }

    # Merge the sequencing file inside the LOGOUTPUT
    awk 'FNR==1 && NR!=1 {next} {print}' sequencing_summary_*.txt > merged_sequencing_summary.txt

    # Merge the telemetry file inside LOGOUTPUT
    jq -s 'add' sequencing_telemetry_*.js > merged_sequencing_telemetry.js

    # Merge them with the already present files
    awk 'FNR==1 && NR!=1 {next} {print}' merged_sequencing_summary.txt > $pathToFinalSummary 
    jq -s 'add' merged_sequencing_telemetry.js > $pathToFinalTelemetry

    # Cleanup
    rm merged_sequencing_summary.txt
    rm merged_sequencing_telemetry.js

    send_telegram_message "File were already present. Run $id .txt and .js file are merged into the \
final one inside the output dir"

else
    echo "First time creating Results file"

    #Go into LOGOUTPUT directory
    cd "$output_dir/output/$id/LOGOUTPUT_"* || { echo "Directory not found"; exit 1; }

    # Merge the sequencing file inside the LOGOUTPUT
    awk 'FNR==1 && NR!=1 {next} {print}' sequencing_summary_*.txt > merged_sequencing_summary.txt

    # Merge the telemetry file inside LOGOUTPUT
    jq -s 'add' sequencing_telemetry_*.js > merged_sequencing_telemetry.js
    
    # Move them
    mv merged_sequencing_summary.txt "$pathToFinalSummary"
    mv merged_sequencing_telemetry.js "$pathToFinalTelemetry"

    send_telegram_message "No file was present. I successfully merged the .txt and .js file for $id and \
moved them inside final output dir"

fi