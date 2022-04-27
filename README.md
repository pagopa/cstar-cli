# cstar-cli

Command Line Interface to manage cstar platform and its verticals

## Prerequisites

The project is managed with [Poetry](https://python-poetry.org/): installation instructions for all platforms are available [here](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions).

If you are using an **M1 MacBook**: install [postgresql](https://www.postgresql.org/) first.
 ```bash
brew install postgresql
```

## Virtualenv initialization

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

### Enrolling payment instruments

```bash
cst bpd paymentinstrument --action enroll --connection-string <CONNSTR> --file <INPUT_FILE>
```

### Creating synthetic hashpans for the Batch Acquirer

```bash
cst rtd transactionfilter --action synthetic_hashpans --pans-prefix "prefix_" --hashpans-qty 20000 --salt <SALT>
```

### Creating synthetic transactions for the Batch Acquirer

See: https://app.gitbook.com/o/KXYtsf32WSKm6ga638R3/s/A5nRaBVrAjc1Sj7y0pYS/acquirer-integration-with-pagopa-centrostella/integration/standard-pagopa-file-transactions

```bash
cst rtd transactionfilter --action synthetic_transactions --pans-prefix "prefix" --pans-qty 20000 --trx-qty 100 --ratio 5
```