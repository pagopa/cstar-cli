#!/bin/sh
# DEPOSITED FILE EQUALITY CHECK
# This script is used to check whether the generated file is equal to the remote deposited file.

if [ $# -ne 4 ] ; then
    echo "Illegal number of parameters (4 mandatory, was $#)" >&2
    echo "usage: script.sh /PATH/TO/LOCAL_OUTPUT.csv /PATH/TO/COMPANY_NAME_UAT.pem /PATH/TO/COMPANY_NAME_UAT.key API_KEY" >&2
    exit 2
fi

# Parameters:
# Path to local output file generated by the Batch Service
LOCAL=$1
# Path to client certificate with .pem extension
CERT=$2
# Path to client private key with .key extension
CERT_KEY=$3
# API Key for RTD Products
API_KEY=$4

URL="https://api.uat.cstar.pagopa.it/rtd/sftp-retrieve/"

# Extract the file name from the path
FILE_NAME="${LOCAL##*/}"

# Use timestamp to make temporary directory name unique
NOW=$(date +%s)
TEMPORARY_DIR="temporary"$NOW

# Create a temporary directory and files
mkdir -p ./"$TEMPORARY_DIR"
mkdir -p ./deposited-remotely
touch ./"$TEMPORARY_DIR"/local.csv

# Make a wget to retrieve the remote file uploaded by the Batch Service
wget --verbose \
    -O ./"$TEMPORARY_DIR"/remote.csv.gz \
    --certificate "$CERT" \
    --private-key "$CERT_KEY" \
    --header 'Ocp-Apim-Subscription-Key: '"$API_KEY" \
    "$URL$FILE_NAME.pgp.0.decrypted.gz"

gunzip ./"$TEMPORARY_DIR"/remote.csv.gz
cp ./"$TEMPORARY_DIR"/remote.csv ./deposited-remotely/"$FILE_NAME"

# Remove CR at the end of the downloaded file, remove record_id columns and sort it
tr -d '\015' < ./"$TEMPORARY_DIR"/remote.csv | cut -d";" -f2- | sort > ./"$TEMPORARY_DIR"/remote_no_record_id.csv

# Remove the first line of the local file and sort it
tail -n +2 "$LOCAL" | sort  > ./"$TEMPORARY_DIR"/local.csv

# Check for content of temporary files
if [ -z "$(cat ./"$TEMPORARY_DIR"/local.csv)" ]
then
  echo "FAIL, ${LOCAL##*/} local file is empty or does not exist."
  exit 2
fi

if [ -z "$(cat ./"$TEMPORARY_DIR"/remote.csv)" ]
then
  echo "FAIL, ${FILE_NAME##*/} remote file is empty or does not exist."
  exit 2
fi

# Store the differences between local and remote files
diff ./"$TEMPORARY_DIR"/local.csv ./"$TEMPORARY_DIR"/remote_no_record_id.csv > ./"$TEMPORARY_DIR"/diff.txt

# If there are no differences the test is passed, otherwise the test is failed and the differences are printed
if [ -z "$(cat ./"$TEMPORARY_DIR"/diff.txt)" ]
then
  echo "PASS, the files are equal!"
  rm -r ./"$TEMPORARY_DIR"
else
  echo "FAIL, found the following differences:"
  cat ./"$TEMPORARY_DIR"/diff.txt
fi