#!/bin/sh
# GENERATED FILE LOCAL EQUALITY CHECK
# This script is used to check whether the generated file is equal to the expected file.

CERT=$1
KEY=$2
API_KEY=$3

if [ $# -ne 3 ]; then
    echo "Illegal number of parameters" >&2
    exit 2
fi

status_code=$(curl -s -o /dev/null -w "%{http_code}" --cert "$CERT" --key "$KEY" --header 'Ocp-Apim-Subscription-Key: '"$API_KEY" https://api.cstar.pagopa.it/rtd/api-key/check)

if [ "${status_code}" -eq 200 ]
then
  echo PASS
else
  echo FAIL
fi