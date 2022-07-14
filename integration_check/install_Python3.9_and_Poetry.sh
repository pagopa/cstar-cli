#!/bin/sh

apt-get update
apt-get install -y software-properties-common python3-distutils
add-apt-repository -y ppa:deadsnakes/ppa
echo "8 41" | apt install -yq python3.9
apt-get install -y python3.9-distutils
wget https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py
echo "y" | python3.9 get-poetry.py