# cstar-cli

Command Line Interface to manage cstar platform and its verticals

## Prerequisites

The project is managed with [Poetry](https://python-poetry.org/): installation instructions for all platforms are available [here](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions).

## Virtualenv initialization

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
pip install src/cstar-cli-core
pip install src/cstar-cli
```

Now the cstar CLI is available as _cst_ command:

```bash
$ cst
usage: __main__.py [-h] {fa,bpd} ...
__main__.py: error: the following arguments are required: subsystem
```
