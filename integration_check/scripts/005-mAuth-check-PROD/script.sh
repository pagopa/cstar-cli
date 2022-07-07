#!/bin/sh
# MAUTH PROD CHECK
# This script is used to check the validity of PROD mAuth certificate.

if [ $# -ne 2 ] ; then
    echo "Illegal number of parameters (2 mandatory, was $#)" >&2
    echo "usage: script.sh /PATH/TO/COMPANY_NAME_PROD.pem /PATH/TO/COMPANY_NAME_PROD.key" >&2
    exit 2
fi

# Parameters:
# Path to client certificate with .pem extension
CERT=$1
# Path to client private key with .key extension
CERT_KEY=$2

# Make a CURL to PROD endpoint with the certificate and key
wget --verbose -O - --certificate "$CERT" --private-key "$CERT_KEY" https://api.cstar.pagopa.it/rtd/mauth/check