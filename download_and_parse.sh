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

log_file=$(echo $url | awk -F'/' '{print $NF}')
if [[ "$log_file" =~ "job-output.txt" ]]; then
    log_dir=$(echo $url | awk -F'/' '{print $9}')
    job_name=$(echo $url | awk -F'/' '{print $8}')
    parser="./tests_times.py"
else
    log_dir=$(echo $url | awk -F'/' '{print $9}')
    job_name=$(echo $url | awk -F'/' '{print $8}')
    parser="./rest_calls_time.py"
fi

dest_dir="$base_path/$job_name/$log_dir"
mkdir -p $dest_dir

wget $url -O "$dest_dir/$log_file"
if [ $? -ne 0 ]; then
    echo "Failed to download file. Exiting..."
    exit 1
fi

# Save destination from where file were downloaded
source_file_name="${log_file}_${SRC_FILE_NAME}"
touch "$dest_dir/$source_file_name"
echo $url > "$dest_dir/$source_file_name"

# Parse downloaded file and store results
results_file_name="${log_file}_${PARSE_RESULTS_FILE_NAME}"
touch "$dest_dir/$results_file_name"
python $parser "$dest_dir/$log_file" > "$dest_dir/$results_file_name"
