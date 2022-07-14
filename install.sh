#!/bin/sh
# Make sure to run this command inside a Poetry shell

python -m pip install --upgrade pip
pip install numpy
pip install pandas
pip install --force-reinstall src/cstar-cli-core
pip install --no-deps --force-reinstall src/cstar-cli
