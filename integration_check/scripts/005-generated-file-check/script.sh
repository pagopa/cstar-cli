#!/bin/sh
# 5 - Generated file equality check
# This script is used to check whether the generated file is equal to the expected file.

if [ $# -ne 2 ]; then
    echo "Illegal number of parameters" >&2
    exit 2
fi

PATH_TO_EXPECTED=$1
PATH_TO_ACTUAL=$2

NOW=$(date +%s)
TEMPORARY_DIR="temporary"$NOW

# Create a temporary directory and files
mkdir ./"$TEMPORARY_DIR" > /dev/null
touch ./"$TEMPORARY_DIR"/expected.csv
touch ./"$TEMPORARY_DIR"/actual.csv

# Sort files
sort < "$PATH_TO_EXPECTED" > ./"$TEMPORARY_DIR"/expected.csv
sort < "$PATH_TO_ACTUAL" > ./"$TEMPORARY_DIR"/actual.csv

# Save differences in a temporary file
diff ./"$TEMPORARY_DIR"/expected.csv ./"$TEMPORARY_DIR"/actual.csv > ./"$TEMPORARY_DIR"/diff.txt

if [ -z "$(cat ./"$TEMPORARY_DIR"/diff.txt)" ]
then
  echo PASS
  rm -r ./"$TEMPORARY_DIR"
else
  echo FAIL
  cat ./"$TEMPORARY_DIR"/diff.txt
fi
