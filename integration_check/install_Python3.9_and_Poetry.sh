#!/bin/sh

apt-get install -y unzip software-properties-common python3-distutils
apt-get update
add-apt-repository -y ppa:deadsnakes/ppa
echo "8 41" | apt install -yq python3.9
apt-get install -y python3.9-distutils
wget -O ./cstar-cli.zip https://github.com/pagopa/cstar-cli/archive/refs/heads/main.zip
unzip cstar-cli.zip
wget https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py
echo "y" | python3.9 get-poetry.py