#!/bin/sh
# DEPOSITED FILE EQUALITY CHECK
# This script is used to check whether the generated file is equal to the remote deposited file.

if [ $# -ne 4 ]; then
    echo "Illegal number of parameters (should be 4)" >&2
    exit 2
fi

LOCAL=$1
CERT=$2
KEY=$3
API_KEY=$4

URL="https://api.dev.cstar.pagopa.it/rtd/sftp-retrieve/"

FILE_NAME="${LOCAL##*/}"

NOW=$(date +%s)
TEMPORARY_DIR="temporary"$NOW


mkdir ./"$TEMPORARY_DIR" > /dev/null
touch ./"$TEMPORARY_DIR"/local.csv
touch ./"$TEMPORARY_DIR"/remote.csv

#echo $URL
#echo $FILE_NAME

#CONTROLLO ASINCRONO

# Get the remote file, remove the record id column and sort it
curl --request GET -sL \
     --url "$URL$FILE_NAME.pgp.0.decrypted" \
     --cert "$CERT" \
     --key "$KEY" \
     --header 'Ocp-Apim-Subscription-Key: '"$API_KEY" \
     --output ./"$TEMPORARY_DIR"/remote.csv


tr -d '\015' < ./"$TEMPORARY_DIR"/remote.csv | cut -d";" -f2- | sort > ./"$TEMPORARY_DIR"/remote_no_record_id.csv

# Remove the first line of the local file and sort it
tail -n +2 "$LOCAL" | sort  > ./"$TEMPORARY_DIR"/local.csv

# Store the differences between local and remote files
diff ./"$TEMPORARY_DIR"/local.csv ./"$TEMPORARY_DIR"/remote_no_record_id.csv > ./"$TEMPORARY_DIR"/diff.txt

# If there are no differences the test is passed, otherwise the test is failed and the differences are printed
if [ -z "$(cat ./"$TEMPORARY_DIR"/diff.txt)" ]
then
  echo PASS
  rm -r ./"$TEMPORARY_DIR"
else
  echo FAIL
  cat ./"$TEMPORARY_DIR"/diff.txt
fi