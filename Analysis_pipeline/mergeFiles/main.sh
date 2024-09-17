#!/bin/bash
# Copyright 2024 Rodolfo Tolloi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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

send_message() {
  local message="$1"
  local chat_id="$CHAT_ID"
  local token="$BC_TOKEN_BOT"

  # Escape special characters for Markdown
  local escaped_message
  escaped_message=$(printf '%s' "$message" | sed 's/[][\.*^$]/\\&/g; s/_/\\_/g; s/`/\\`/g; s/*/\\*/g; s/~(?!\()/\\~/g; s/\n/\\n/g;')

  curl -s -X POST "https://api.telegram.org/bot$token/sendMessage" \
    -d "chat_id=$chat_id" \
    -d "text=$escaped_message" \
    -d "parse_mode=MarkdownV2"
}

# Get samplesheet path and id from arguments
samplesheet_path="$1"
id="$2"

send_message("-----ALIGNMENT-RUN-----\n Started analysis run for $id")

# Assuming you have a command line tool or another way to extract metadata from the samplesheet
output_dir=$(jq -r '.metadata.outputLocation' "$samplesheet_path")

pathToFinalBasecalling="$output_dir/BasecallingResults.fastq"
pathToFinalAlignment="$output_dir/AlignmentResults.bam"

# Check if the result files already exist in the directory
if check_ResultsFiles_in_directory "$output_dir"; then
    echo "Results file are already present!"

    # Concatenate fastq files
    cat_command="cat $output_dir/output/$id/run_${id}_merged.fastq $pathToFinalBasecalling > tmp.fastq"
    samtools_command="samtools merge -o $pathToFinalAlignment $pathToFinalAlignment $output_dir/output/$id/bam/run_${id}.bam"

    # Execute the cat command
    if eval "$cat_command"; then
        echo "Successfully concatenated fastq files"
        mv tmp.fastq $pathToFinalBasecalling
    else
        echo "Error concatenating fastq files"
        exit 1
    fi

    # Execute the samtools merge command
    if eval "$samtools_command"; then
        echo "Successfully merged BAM files"
    else
        echo "Error merging BAM files"
        exit 1
    fi

else
    echo "First time creating Results file"

    # Move the initial .fastq and .bam files to final locations
    cp "$output_dir/output/$id/run_${id}_merged.fastq" "$pathToFinalBasecalling"
    cp "$output_dir/output/$id/bam/run_${id}.bam" "$pathToFinalAlignment"
fi
