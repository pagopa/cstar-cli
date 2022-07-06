#!/bin/sh
# API Key UAT CHECK
# This script is used to check the validity of UAT mAuth  certificate and API Key.

if [ $# -ne 3 ]; then
    echo "Illegal number of parameters (expected 3)" >&2
    exit 2
fi

CERT=$1
KEY=$2
API_KEY=$3

# Make a CURL to UAT endpoint with the certificate, key and API Key
curl -v --cert "$CERT" --key "$KEY" --header 'Ocp-Apim-Subscription-Key: '"$API_KEY" https://api.uat.cstar.pagopa.it/rtd/api-key/check