#!/bin/bash
CERT=$1
KEY=$2

status_code=$(curl -s -o /dev/null -w "%{http_code}" --cert $CERT --key $KEY https://api.uat.cstar.pagopa.it/rtd/mauth/check)

if [ ${status_code} -eq 200 ]
then
  echo PASS
else
  echo FAIL
fi