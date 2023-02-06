# cstar-cli

Command Line Interface to manage cstar platform and its verticals

## Prerequisites

The project is managed with [Poetry](https://python-poetry.org/): installation instructions for all platforms are
available [here](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions).

## Virtualenv initialization

> Make sure to be in the root of this project.

Open a shell and type the following:

```bash
poetry install
```

This will ensure an isolated virtualenv will exists for this project and required dependencies will be installed within.

## Using the cstar CLI

Enter the virtualenv with the command:

```bash
poetry shell
```

If is the first time or changes have been made to the codebase install the packages:

```bash
./install.sh
```

Now the cstar CLI is available as _cst_ command:

```bash
cst <VERTICAL> <DOMAIN> --action <ACTION> [COMMAND PARAMETERS ...]
```

## Example(s)

## BPD

### Enrolling payment instruments

```bash
cst bpd paymentinstrument --action enroll --connection-string <CONNSTR> --file <INPUT_FILE>
```

---

## RTD

### Creating synthetic hashpans for the Batch Service

```bash
cst rtd transactionfilter --action synthetic_hashpans --pans-prefix "prefix_" --hashpans-qty 20000 --salt <SALT>
```

### Creating synthetic transactions for the Batch Service.

>
See: https://app.gitbook.com/o/KXYtsf32WSKm6ga638R3/s/A5nRaBVrAjc1Sj7y0pYS/acquirer-integration-with-pagopa-centrostella/integration/standard-pagopa-file-transactions

#### Unencrypted

```bash
cst rtd transactionfilter --action synthetic_transactions --sender 12345 --pans-prefix "prefix_" --pans-qty 20000 --trx-qty 100 --ratio 5 --pos-number 10000 --salt <SALT> --input-hashpans ~/hashpans_file.txt
```

#### Encrypted, with specified output directory and public key file.

```bash
cst rtd transactionfilter --action synthetic_transactions --pans-prefix "prefix_" --pans-qty 20000 --trx-qty 100 --ratio 5 --pos-number 10000 --salt <SALT> --out-dir /tmp --pgp --key ~/certificates/public.key --input-hashpans ~/hashpans_file.txt
```

### Creating synthetic cards for the Enrolled Payment Instrument microservice

```bash
cst rtd transactionfilter --action synthetic_cards --pans-prefix "prefix_" --crd-qty 10 --par RANDOM  --max-num-children 5 --state READY
```

Params </br>

--pans-prefix: synthetic PANs will be generated as "{PREFIX}{NUMBER}". </br>
--crd-qty: the number of cards to generate in output. </br>
--max-num-children: the max number of hashpans card children for each card. </br>
--num-children: the precise number of hashpans card children for each card. </br>
--par: par flag (YES | NO | RANDOM ->  defult:RANDOM). </br>
--state: state of the cards (READY | REVOKED | ALL -> default:ALL). </br>
--salt: the salt to use when performing PAN hashing ( default: SALT876). </br>
--revoked-percentage: number between 0 and 100 for the percentage of revoked cards (default=10%)

Just pans-prefix and crd-qty are mandatory. </br>
If you want hashpan children you need to use ONE parameters between --max-num-children and --num-children. </br>
If no one of these two are choosen all the cards records will not have children hashpan. </br>

### Upload transaction file

```bash
cst rtd transactionupload --action upload --env dev --api-key "xxx" --key "path/to/private.key" --cert "path/to/certificate.pem"  --file "path/to/CSTAR.*.TRNLOG.*.csv"
```

Params </br>

--env: environment `dev`, `uat`, `prod` </br>
--api-key: APIM subscription key </br>
--key: private key for mauth </br>
--cert: certificate for mauth </br>
--file: transaction file in .csv. It will automatically encrypt using pgp

---

## TAE

#### Creating synthetic aggregations like the ones produced by the Batch Acquirer for AdE.

> To generate 1MB of aggregates it takes about 9K aggregations.

> With the shuffling flag it takes more time to generate the file.

#### Unencrypted

```bash
cst tae transactionaggregate --action aggregate_transactions --aggr-qty 9000 --reverse-ratio 100 --ratio-dirty-pos-type 30 --ratio-dirty-vat 20 --shuffle
```

#### Encrypted, with specified output directory and public key file.

```bash
cst tae transactionaggregate --action aggregate_transactions --aggr-qty 9000 --reverse-ratio 100 --ratio-dirty-pos-type 30 --ratio-dirty-vat 20 --shuffle --out-dir /tmp --pgp --key ~/certificates/public.key
```

### Creating synthetic acks like the ones sent by AdE to CSTAR, according to the interface agreement.

#### Unzipped

```bash
cst tae results --action synthetic_results --res-qty 100
```

#### Zipped

```bash
cst tae results --action synthetic_results --res-qty 100 --gzip
```

### Creating synthetic wrong record reports like the ones sent by Cstar to senders.

```bash
cst tae registryreports --action synthetic_reports --rep-qty 100
```

---

## Sender

### Create input transactions and corresponding aggregates' output files (like the one produced by a run of batch service).

**For acquirers:**

```bash
cst sender aggregates --sender <ABI> --action trx_and_aggr --aggr-qty 10
```

---
**For schemas (Bancomat) and technical senders (Satispay, Sumup, BancomatPay, iCard):**

```bash
cst sender aggregates --sender {COBAN, STPAY, SUMUP, BPAY1, ICARD} --action trx_and_aggr --aggr-qty 10
```

This will also test the translation of technical ABI to acquirer fiscal code.

---

### Check the equality of the generated files with the ones produced by the batch service.

```bash
cst sender aggregates --action diff --files /path/to/files/produced/by/batch/service /path/to/files/produced/by/CSTAR/CLI
```

## Regression testing

### To check for execution errors on commands you can run the following:

```bash
sh ./test/run-all.sh
```

## IDPAY

### Creates synthetic fiscal codes, their synthetic payment instruments (encrypted with Payment Manager public key) and a transaction file associated with them.

```bash
cst idpay idpaydataset --action dataset_and_transactions --env dev --api-key aaa000aaa --key ~/certificates/private.key --cert ~/certificates/public.key --PM-pubk ./PM-public.asc
```

Parameters: </br>

- `--action ACTION`: Action to perform with the invocation of the command.
- `--num-fc NUM_FC`: Number of fiscal codes generated.
- `--min-pan-per-fc MIN_PAN_PER_FC`: Minimum number of payment instruments per fiscal code.
- `--max-pan-per-fc MAX_PAN_PER_FC`: Maximum number of payment instruments per fiscal code.
- `--trx-per-fc TRX_PER_FC`: Number of transactions per fiscal code.
- `--sender-code SENDER_CODE`: Sender code that will appear in transactions' file.
- `--acquirer-code ACQUIRER_CODE`: Acquirer code that will appear in transactions' file.
- `--datetime DATETIME`: Date and time in format yyyy-MM-ddTHH:mm:ss.SSSz of every transaction.
- `--min-amount MIN_AMOUNT`: Minimum amount of euro cents of a single transaction.
- `--max-amount MAX_AMOUNT`: Maximum amount of euro cents of a single transaction.
- `--mcc MCC`: Merchant category code used in every transaction.
- `--out-dir OUT_DIR`: Output destination of files generated.
- `--env {dev,uat,prod}`: Environment.
- `--api-key API_KEY`: API key cpable to using RTD_API_Product.
- `--key KEY`: Private key of the muthual authentication certificate.
- `--cert CERT`: Public key of the muthual authentication certificate.
- `--PM-pubk PM_PUBK`: Path to the public key of the Payment Manager.
- `--PM-salt PM_SALT`: Current salt of the Payment Manager. If not specified the API is called.
- `--RTD-pubk RTD_PUBK`: Path to the public key of the RTD. If not specified the API is called.

### The ouptut produced is:

- `fc.csv`: Contains testing Fiscal Codes generated.
- `pans.csv`: Contains testing payment instruments.
- `fc_pan.csv`: Contains (Fiscal Code, PAN) association.
- `fc_pgpans.csv`: Contains (Fiscal Code, PGPAN) association.
- `pan_hpans`: Contains (PAN, HPAN) association.
- `CSTAR.<SENDER_CODE>.TRNLOG.<DATE>.<TIME>.001.01.csv`: Transactions file associated to the dataset generated.
- `CSTAR.<SENDER_CODE>.TRNLOG.<DATE>.<TIME>.001.01.csv.pgp`: Transactions file associated to the dataset generated
  encrypted with RTD public key.

### Creates synthetic transactions given a file of PAN-HPAN couples.

```bash
cst idpay idpaytransactions --action transactions --env dev --trx-qty 10 --api-key aaa000aaa --key ~/certificates/private.key --cert ~/certificates/public.key --datetime 2023-01-01T00:00:00.000+00:00 --input-pans-hashpans ./pans_hpans.csv
```
- `--action ACTION`: Action to perform with the invocation of the command.
- `--trx-qty TRX_QTY`: Number of transactions desired.
- `--sender-code SENDER_CODE`: Sender code that will appear in transactions' file.
- `--acquirer-code ACQUIRER_CODE`: Acquirer code that will appear in transactions' file.
- `--datetime DATETIME`: Date and time in format yyyy-MM-ddTHH:mm:ss.SSSz of every transaction.
- `--min-amount MIN_AMOUNT`: Minimum amount of euro cents of a single transaction.
- `--max-amount MAX_AMOUNT`: Maximum amount of euro cents of a single transaction.
- `--mcc MCC`: Merchant category code used in every transaction.
- `--out-dir OUT_DIR`: Output destination of files generated.
- `--env {dev,uat,prod}`: Environment.
- `--api-key API_KEY`: API key cpable to using RTD_API_Product.
- `--key KEY`: Private key of the muthual authentication certificate.
- `--cert CERT`: Public key of the muthual authentication certificate.
- `--input-pans-hashpans INPUT_PANS_HASHPANS`: Path of pans-hashpans couples file used as payment methods in transactions' file.
- `--hpans-head HPANS_HEAD`: Takes the first N HPANs from HPANs file. If not specified all the HPANs are taken.
- `--RTD-pubk RTD_PUBK`: Path to the public key of the RTD, if not specified the API is called.

### The ouptut produced is:

- `CSTAR.<SENDER_CODE>.TRNLOG.<DATE>.<TIME>.001.01.csv`: Transactions file associated to the dataset given as input.
- `CSTAR.<SENDER_CODE>.TRNLOG.<DATE>.<TIME>.001.01.csv.pgp`: Transactions file associated to the dataset given as input
  encrypted with RTD public key.

### Creates a synthetic reward file based on payment provision.

```bash
cst idpay idpayrewards --action rewards --payment-provisions-export ./payment-provisions.csv --perc-succ 0.4 --perc-dupl 0.1
```

Parameters: </br>

- `--payment-provisions-export PAYMENT_PROVISIONS_EXPORT`: Path to input payment provisions exported by IDPay.
- `--exec-date EXEC_DATE`: Date in format yyyy-MM-dd of reward process.
- `--perc-succ PERC_SUCC`: Percentage of successful rewards.
- `--perc-dupl PERC_DUPL`: Percentage of duplicates records.
- `--out-dir OUT_DIR`: Output destination of files generated.

### The ouptut produced is:

- `reward-dispositive-<DATE>T<TIME>.csv`: Contains rewards based on uniqueID of payment provision provided.
