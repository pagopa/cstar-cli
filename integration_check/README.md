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

## 3. Equality check between produced and expected files

The third steps checks for correct functioning of the batch service.

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
sh ./integration_check/scripts/004-remote-file-check-UAT/script.sh /PATH/TO/LOCAL_FILE.csv /PATH/TO/ACME_UAT.certificate.pem /PATH/TO/ACME_UAT.key UAT_API_KEY
```
The execution will print the result of the check.