#!/bin/bash
set -ex

current_dir=$(pwd)

if ! command -v codeql &> /dev/null
then
    echo "CodeQL CLI is not installed. Installing CodeQL CLI..."
    mkdir -p ~/codeql
    cd ~/codeql
    wget https://github.com/github/codeql-action/releases/download/codeql-bundle-v2.15.0/codeql-bundle.tar.gz
    tar --strip-components=1 -xzf codeql-bundle.tar.gz
    rm codeql-bundle.tar.gz
    echo 'export PATH=~/codeql:$PATH' >> ~/.bashrc
    source ~/.bashrc
    cd "$current_dir"
fi

echo "Installing Growlithe..."

if ! dpkg -s python3.11-venv &> /dev/null
then
    echo "python3.11-venv is not installed. Installing python3.11-venv..."
    sudo apt-get install python3.11-venv
fi

python3.11 -m venv venv
source venv/bin/activate
pip install -e .
