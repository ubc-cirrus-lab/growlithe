#!/bin/bash

set -ex

queries=(file requests socket boto3)

cd ./high-level-flow

wget https://github.com/github/codeql-cli-binaries/releases/download/v2.12.3/codeql-linux64.zip
unzip codeql-linux64.zip
export PATH=$PATH:$(pwd)/codeql

cd ./code
mkdir -p query_results

codeql pack install
python -m pip install -r requirements.txt

codeql database create codeqldb --language=python --overwrite
for query in "${queries[@]}"; do
    codeql database analyze codeqldb --format=csv --output=query_results/$query.csv queries/$query.ql
done