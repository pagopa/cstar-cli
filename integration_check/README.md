# CSTAR-CLI - Integration with CSTAR checks

In this file are documented the steps to follow in order to fulfill the first two steps of integration with CSTAR.

Every test results in either `PASS` (200 as response status) or `FAIL` (400 or 401 as response status).

## 1. Mutual Authentication certificate validity check UAT

The first step checks the validity of the client certificate.

This can be assessed with a call to an [enpoint](https://api.uat.cstar.pagopa.it/rtd/mauth/check) with a valid certificate and key.

From the project root move to the directory ./scripts/001-mAuth-check-UAT .

Then run the script with the following command (after customization):
```bash
sh ./integration_check/scripts/001-mAuth-check-UAT/script.sh /PATH/TO/COMPANY_NAME_UAT.certificate.pem /PATH/TO/COMPANY_NAME_UAT.key
```

The execution will print the result of the check.

## 2. API Key validity check UAT

The second step checks the validity of the client certificate and API Key.

This can be assessed with a call to an [enpoint](https://api.uat.cstar.pagopa.it/rtd/api-key/check) with a valid API Key.

From the project root move to the directory ./scripts/002-API-key-check-UAT.

Then run the script with the following command (after customization):
```bash
sh ./integration_check/scripts/002-API-key-check-UAT/script.sh /PATH/TO/COMPANY_NAME_UAT.certificate.pem /PATH/TO/COMPANY_NAME_UAT.key UAT_API_KEY
```
The execution will print the result of the check.

## 3. Equality check between produced and expected files

The third step checks for correct functioning of the batch service.

Given the previously generated input file (see root README in Sender section), you can run the batch service.
Once the process is completed, shut the instance down and locate the ADE output file.

Then pass the path to it, in pair with the previously produced expected output, to the script.

From the project root, run the script with the following (properly customized) command:
```bash
sh ./integration_check/scripts/003-expected-file-check-UAT/script.sh /PATH/TO/EXPERECTED_FILE.csv.expected /PATH/TO/PRODUCED_FILE.csv
```
The execution will print the result of the check.

## 4. Equality check between produced and deposited remote files

The forth step checks for correct functioning of the batch service.

Once the previous test is passed, pass the path to the file generated with the batch service to the script.

> Note that the backend needs time to process the file.
> Therefore, the 

From the project root, run the script with the following (properly customized) command:
```bash
sh ./integration_check/scripts/004-remote-file-check-UAT/script.sh /PATH/TO/LOCAL_FILE.csv /PATH/TO/COMPANY_NAME_UAT.certificate.pem /PATH/TO/COMPANY_NAME_UAT.key UAT_API_KEY
```
The execution will print the result of the check.

## 5. Mutual Authentication certificate validity check PROD

The first step checks the validity of the client certificate.

This can be assessed with a call to an [enpoint](https://api.cstar.pagopa.it/rtd/mauth/check) with a valid certificate and key.

From the project root run the script with the following command:
```bash
sh ./integration_check/scripts/005-mAuth-check-PROD/script.sh /PATH/TO/COMPANY_NAME_PROD.certificate.pem /PATH/TO/COMPANY_NAME_PROD.key
```
The execution will print the result of the check.

## 6. API Key validity check PROD

The second step checks the validity of the API Key.

This can be assessed with a call to an [enpoint](https://api.cstar.pagopa.it/rtd/api-key/check) with a valid API Key.

From the project root run the script with the following command:
```bash
sh ./integration_check/scripts/006-API-key-check-PROD/script.sh /PATH/TO/COMPANY_NAME_PROD.certificate.pem /PATH/TO/COMPANY_NAME_PROD.key PROD_API_KEY
```
The execution will print the result of the check.