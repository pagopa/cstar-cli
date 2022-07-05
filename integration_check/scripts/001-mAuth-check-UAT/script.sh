#!/bin/sh
# MAUTH UAT CHECK
# This script is used to check the validity of UAT mAuth certificate.

if [ $# -ne 2 ] ; then
    echo "Illegal number of parameters (expected 2)" >&2
    exit 2
fi

CERT=$1
KEY=$2

status_code=$(curl -s -o /dev/null -w "%{http_code}" --cert "$CERT" --key "$KEY" https://api.uat.cstar.pagopa.it/rtd/mauth/check)

if [ "${status_code}" -eq 200 ]
then
  echo PASS
else
  echo FAIL
fi