#!/bin/sh
# EXTRACT ADE ACK
# This script is used to extract a fake ADE ACK file from the file deposited from the batch service to SFTP.
# Once extracted the file is uploaded to the SFTP server where the batch service will download it.

if [ $# -ne 4 ] ; then
    echo "Illegal number of parameters (4 mandatory, was $#)" >&2
    echo "usage: script.sh /PATH/TO/DOWNLOADED.csv /PATH/TO/COMPANY_NAME_UAT.pem /PATH/TO/COMPANY_NAME_UAT.key API_KEY" >&2
    exit 2
fi

## Parameters:
## Path to local output file downloaded during the previous script.
LOCAL=$1
# Path to client certificate with .pem extension
CERT=$2
# Path to client private key with .key extension
CERT_KEY=$3
# API Key for RTD Products
API_KEY=$4

# Number of lines extracted at random that will form the fake ADE ACK file.
NUM_RANDOM_ACKED_LINES=5

URL="https://api.uat.cstar.pagopa.it/rtd/sftp-deposit/"

# Extract the file name from the path
FILE_NAME="${LOCAL##*/}"

# Compose the ADE ACK filename
ADE_ACK_NAME="CSTAR.ADEACK.$(echo "$FILE_NAME" | cut -d'.' -f2 -f4 -f5 -f6 -f7)"

# Use timestamp to make temporary directory name unique
NOW=$(date +%s)
TEMPORARY_DIR="temporary"$NOW

# Create a temporary directory and files
mkdir -p ./"$TEMPORARY_DIR"
mkdir -p ./generated/ade-acks

# Take NUM_RANDOM_ACKED_LINES random lines and save them in a file that will be uploaded
shuf -n "$NUM_RANDOM_ACKED_LINES" "$LOCAL" > "./$TEMPORARY_DIR/extracted_lines.csv"

# Remove zero-width-spacing and CR at the end of the downloaded file
tr -d '\015' < "./$TEMPORARY_DIR/extracted_lines.csv" | sed 's/\xef\xbb\xbf//g' > "./$TEMPORARY_DIR/extracted_lines_cleaned.csv"

# Counters for ade acks errors and success
i=0

# Generate a fake ADE ACK record for each line
while read -r p; do
  if [ $i -eq 0 ]
    then
      echo "$p" | awk -F ";" '{print($1";0;")}' >> "./$TEMPORARY_DIR/$ADE_ACK_NAME"  else
  fi
  if [ $i -eq 1 ]
    then
      echo "$p" | awk -F ";" '{print($1";1;")}' >> "./$TEMPORARY_DIR/$ADE_ACK_NAME"  else
      echo "$p" | awk -F ";" '{print($10";"$11";"$12";"$9";1;")}' >> "./$TEMPORARY_DIR/$ADE_ACK_NAME.expected"
  fi
  if [ $i -eq 2 ]
    then
      echo "$p" | awk -F ";" '{print($1";3;")}' >> "./$TEMPORARY_DIR/$ADE_ACK_NAME"  else
      echo "$p" | awk -F ";" '{print($10";"$11";"$12";"$9";3;")}' >> "./$TEMPORARY_DIR/$ADE_ACK_NAME.expected"
    else
      echo "$p" | awk -F ";" '{print($1";4;1201|1302")}' >> "./$TEMPORARY_DIR/$ADE_ACK_NAME"
      echo "$p" | awk -F ";" '{print($10";"$11";"$12";"$9";4;1201|1302")}' >> "./$TEMPORARY_DIR/$ADE_ACK_NAME.expected"
  fi
done < "./$TEMPORARY_DIR/extracted_lines_cleaned.csv"

# Check for content of temporary file
if [ -z "$(cat "./$TEMPORARY_DIR/$ADE_ACK_NAME")" ]
then
  echo "FAIL, ./$TEMPORARY_DIR/$ADE_ACK_NAME file is empty or does not exist."
  exit 2
fi

if [ -z "$(cat "./$TEMPORARY_DIR/$ADE_ACK_NAME.expected")" ]
then
  echo "FAIL, ./$TEMPORARY_DIR/$ADE_ACK_NAME.expected file is empty or does not exist."
  exit 2
fi

# Save the file in the generated directory for the next script
cp "./$TEMPORARY_DIR/$ADE_ACK_NAME.expected" "./generated/ade-acks/$ADE_ACK_NAME.expected"

gzip "./$TEMPORARY_DIR/$ADE_ACK_NAME"

# Upload the file through the APIM
wget --verbose \
    -O - \
    --method=PUT \
    --body-file "./$TEMPORARY_DIR/$ADE_ACK_NAME.gz" \
    --certificate "$CERT" \
    --private-key "$CERT_KEY" \
    --header 'Ocp-Apim-Subscription-Key: '"$API_KEY" \
    "$URL$ADE_ACK_NAME.gz"

# Check for content of temporary file
if [ -z "$(cat "./generated/ade-acks/$ADE_ACK_NAME.expected")" ]
then
  echo "FAIL, ./generated/ade-acks/$ADE_ACK_NAME.expected file is empty or does not exist."
  exit 2
fi

rm -rf "./$TEMPORARY_DIR"
echo 'Done'
