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


# Check input arguments
if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <directory> <output_file> <max_workers>"
  exit 1
fi

input_dir="$1"
output_file="$2"
max_workers="$3"

# Ensure the directory exists
if [[ ! -d "$input_dir" ]]; then
  echo "Directory $input_dir does not exist"
  exit 1
fi

# Ensure the directory is not empty
files=("$input_dir"/*)
if [[ ${#files[@]} -eq 0 ]]; then
  echo "Directory $input_dir is empty"
  exit 1
fi

# Ensure the max_workers is a valid number
if ! [[ "$max_workers" =~ ^[0-9]+$ ]] || [[ "$max_workers" -le 0 ]]; then
  echo "Invalid worker limit: $max_workers"
  exit 1
fi

# Total number of files
num_files=${#files[@]}

# If there are more workers than files, adjust worker count
if [[ $max_workers -gt $num_files ]]; then
  max_workers=$num_files
fi

# Calculate how many files each worker should process
files_per_worker=$(( (num_files + max_workers - 1) / max_workers )) # Round up division

# Temporary directory to store intermediate files
tmp_dir=$(mktemp -d)

echo "Processing $num_files files in $input_dir with a max of $max_workers workers..."

# Function to cat a chunk of files
cat_chunk() {
  local chunk_num=$1
  shift
  local tmp_file="$tmp_dir/tmp_merged_$chunk_num"
  cat "$@" > "$tmp_file"
}

# Create workers, each processing an appropriate share of files
for (( i=0; i<max_workers; i++ )); do
  start=$(( i * files_per_worker ))
  chunk_files=( "${files[@]:start:files_per_worker}" )

  if [[ ${#chunk_files[@]} -gt 0 ]]; then
    echo "Worker $i processing files: ${chunk_files[*]}"
    cat_chunk "$i" "${chunk_files[@]}" &
  fi
done

# Wait for all workers to finish
wait

# Final merge of temporary files
cat "$tmp_dir"/tmp_merged_* > "$output_file"

# Clean up temporary directory
rm -r "$tmp_dir"

echo "All files merged into $output_file"
