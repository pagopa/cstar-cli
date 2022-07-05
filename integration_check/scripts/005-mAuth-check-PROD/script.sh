#!/bin/sh
# MAUTH PROD CHECK
# This script is used to check the validity of PROD mAuth certificate.

CERT=$1
KEY=$2

if [ $# -ne 2 ]; then
    echo "Illegal number of parameters" >&2
    exit 2
fi

status_code=$(curl -s -o /dev/null -w "%{http_code}" --cert "$CERT" --key "$KEY" https://api.cstar.pagopa.it/rtd/mauth/check)

if [ "${status_code}" -eq 200 ]
then
  echo PASS
else
  echo FAIL
fi