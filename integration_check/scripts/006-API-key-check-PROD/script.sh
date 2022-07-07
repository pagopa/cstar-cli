#!/bin/sh
# API Key PROD CHECK
# This script is used to check the validity of PROD mAuth  certificate and API Key.

if [ $# -ne 3 ] ; then
    echo "Illegal number of parameters (3 mandatory, was $#)" >&2
    echo "usage: script.sh /PATH/TO/ACME_PROD.pem /PATH/TO/ACME_PROD.key API_KEY" >&2
    exit 2
fi

# Parameters:
# Path to client certificate with .pem extension
CERT=$1
# Path to client private key with .key extension
CERT_KEY=$2
# API Key for RTD Products
API_KEY=$3

if [ "${status_code}" -eq 200 ]
then
  echo PASS
else
  echo FAIL
fi