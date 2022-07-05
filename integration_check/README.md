# CSTAR-CLI - Integration with CSTAR checks

In this file are documented the steps to follow in order to fulfill the first two steps of integration with CSTAR.

Every test results in either `PASS` (200 as response status) or `FAIL` (400 or 401 as response status).

## 1. Mutual Authentication certificate validity check

The first steps checks the validity of the client certificate.

This can be assessed with a call to an [enpoint](https://api.uat.cstar.pagopa.it/rtd/mauth/check) with a valid certificate and key.

From the project root run the script with the following command:
```bash
bash ./integration_check/scripts/001-mAuth-check/script.sh /PATH/TO/ACME.certificate.pem /PATH/TO/ACME.key
```
The execution will print the result of the check.

## 2. API Key validity check

The second steps checks the validity of the API Key.

This can be assessed with a call to an [enpoint](https://api.uat.cstar.pagopa.it/rtd/api-key/check) with a valid API Key.

From the project root run the script with the following command:
```bash
bash ./integration_check/scripts/002-API-key-check/script.sh /PATH/TO/ACME.certificate.pem /PATH/TO/ACME.key API_KEY
```
The execution will print the result of the check.