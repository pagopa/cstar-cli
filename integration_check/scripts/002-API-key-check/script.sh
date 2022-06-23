#!/bin/bash
CERT=$1
KEY=$2
API_KEY=$3

status_code=$(curl -s -o /dev/null -w "%{http_code}" --cert $CERT --key $KEY --header 'Ocp-Apim-Subscription-Key: '$API_KEY https://api.uat.cstar.pagopa.it/rtd/api-key/check)

if [ ${status_code} -eq 200 ]
then
  echo PASS
else
  echo FAIL
fi