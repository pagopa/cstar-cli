#!/bin/sh
# API Key UAT CHECK
# This script is used to check the validity of UAT mAuth  certificate and API Key.

if [ $# -ne 3 ] ; then
    echo "Illegal number of parameters (3 mandatory, was $#)" >&2
    echo "usage: script.sh /PATH/TO/COMPANY_NAME_UAT.pem /PATH/TO/COMPANY_NAME_UAT.key API_KEY" >&2
    exit 2
fi

# Parameters:
# Path to client certificate with .pem extension
CERT=$1
# Path to client private key with .key extension
CERT_KEY=$2
# API Key for RTD Products
API_KEY=$3

URL="https://api.uat.cstar.pagopa.it/rtd/api-key/check"

# Make a wget to UAT endpoint with the certificate, key and API Key
wget --verbose \
    -O - \
    --certificate "$CERT" \
    --private-key "$CERT_KEY" \
    --header 'Ocp-Apim-Subscription-Key: '"$API_KEY" \
    $URL
