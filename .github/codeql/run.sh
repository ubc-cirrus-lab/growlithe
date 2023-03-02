#!/bin/bash

set -ex

queries=(file requests socket boto3)

cd ./high-level-flow

sudo apt install python3-pip
wget https://github.com/github/codeql-cli-binaries/releases/download/v2.12.3/codeql-linux64.zip
unzip codeql-linux64.zip
export PATH=$PATH:$(pwd)/codeql

cd ./code
mkdir -p query_results

codeql pack install
pip3 install -r requirements.txt

codeql database create codeqldb --language=python --overwrite
for query in "${queries[@]}"; do
    codeql database analyze codeqldb --format=csv --output=query_results/$query.csv queries/$query.ql
done