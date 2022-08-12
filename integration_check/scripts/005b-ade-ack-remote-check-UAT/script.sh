#!/bin/sh
# GENERATED AND DOWNLOADED ADE ERROR FILE EQUALITY CHECK
# This script is used to check whether the downloaded ADE error file/s is equal to the expected one.

if [ $# -ne 2 ] ; then
    echo "Illegal number of parameters (2 mandatory, was $#)" >&2
    echo "usage: script.sh /PATH/TO/EXPECTED_ADE_ERROR.csv.expected /PATH/TO/ADE_ERROR/DIRECTORY" >&2
    exit 2
fi

# Parameters:
# Path to expected output file generated with the CLI
PATH_TO_EXPECTED=$1
# Path to actual output file generated by the Batch Service
PATH_TO_ACKS=$2

# Use timestamp to make temporary directory name unique
NOW=$(date +%s)
TEMPORARY_DIR="temporary"$NOW

# Create a temporary directory and files
mkdir -p ./"$TEMPORARY_DIR"
touch ./"$TEMPORARY_DIR"/expected.csv
touch ./"$TEMPORARY_DIR"/actual_aggr.csv


ACK_FILES="$PATH_TO_ACKS/*"

# Aggregate all the downloaded ADE error files into one file
for f in $ACK_FILES
do
  echo "Processing $f file..."
  cat "$f" >> ./"$TEMPORARY_DIR"/actual_aggr.csv
done

# Sort files
sort < "$PATH_TO_EXPECTED" > ./"$TEMPORARY_DIR"/expected.csv
sort < ./"$TEMPORARY_DIR"/actual_aggr.csv > ./"$TEMPORARY_DIR"/actual_sort_aggr.csv

# Check for content of temporary files
if [ -z "$(cat ./"$TEMPORARY_DIR"/expected.csv)" ]
then
  echo "FAIL, ${PATH_TO_EXPECTED##*/} file is empty or does not exist."
  rm -r ./"$TEMPORARY_DIR"
  exit 2
fi

if [ -z "$(cat ./"$TEMPORARY_DIR"/actual_sort_aggr.csv)" ]
then
  echo "FAIL, ${PATH_TO_ACTUAL##*/} file is empty or does not exist."
  rm -r ./"$TEMPORARY_DIR"
  exit 2
fi

# Save differences in a temporary file
diff ./"$TEMPORARY_DIR"/expected.csv ./"$TEMPORARY_DIR"/actual_sort_aggr.csv > ./"$TEMPORARY_DIR"/diff.txt

# Check if there are differences
if [ -z "$(cat ./"$TEMPORARY_DIR"/diff.txt)" ]
then
  echo "PASS, the files are equal!"
  rm -r ./"$TEMPORARY_DIR"
else
  echo "FAIL, found the following differences:"
  cat ./"$TEMPORARY_DIR"/diff.txt
fi
