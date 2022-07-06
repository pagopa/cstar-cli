#!/bin/sh
# MAUTH UAT CHECK
# This script is used to check the validity of UAT mAuth certificate.

if [ $# -ne 2 ] ; then
    echo "Illegal number of parameters (2 mandatory, was $#)" >&2
    echo "usage: script.sh /PATH/TO/ACME_UAT.pem /PATH/TO/ACME_UAT.key" >&2
    exit 2
fi

# Parameters:
# Path to client certificate with .pem extension
CERT=$1
# Path to client private key with .key extension
KEY=$2

status_code=$(curl -s -o /dev/null -w "%{http_code}" --cert "$CERT" --key "$KEY" https://api.uat.cstar.pagopa.it/rtd/mauth/check)

if [ "${status_code}" -eq 200 ]
then
  echo PASS
else
  echo FAIL
fi