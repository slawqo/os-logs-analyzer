#!/bin/bash

# Script to download and stores downloaded logs in specific directory
# It will also store in same directory, in file $SRC_FILE_NAME url from which
# logs were downloaded.
# After download logs it will also run parser to parse this log and store
# results in same directory.
# If name of file to download contains "job-output.txt" then it will run
# tests_times.py, otherwise it will run rest_calls_time.py script
#
# Usage:
# ./download_and_parse.sh <path_to_store_logs> <url_to_download>


SRC_FILE_NAME="source"
PARSE_RESULTS_FILE_NAME="parsed_results"

base_path=$1
url=$2

log_dir=$(echo $url | awk -F'/' '{print $(NF-1)}')
log_file=$(echo $url | awk -F'/' '{print $NF}')

dest_dir="$base_path/$log_dir"

mkdir -p $dest_dir
wget $url -O "$dest_dir/$log_file"
if [ $? -ne 0 ]; then
    echo "Failed to download file. Exiting..."
    exit 1
fi

echo $url >> "$dest_dir/$SRC_FILE_NAME"

if [[ "$log_file" =~ "job-output.txt" ]]; then
    python ./tests_times.py "$dest_dir/$log_file" >> "$dest_dir/$PARSE_RESULTS_FILE_NAME"
else
    python ./rest_calls_time.py "$dest_dir/$log_file" >> "$dest_dir/$PARSE_RESULTS_FILE_NAME"
fi
