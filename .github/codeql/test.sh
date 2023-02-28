#!/bin/bash

set -ex

cd ./high-level-flow/code
queries=(file requests socket boto3)
mkdir -p query_results

wget https://github.com/github/codeql-cli-binaries/releases/download/v2.12.3/codeql-linux64.zip
unzip codeql-linux64.zip
export PATH=$PATH:$(pwd)/codeql

codeql pack install
codeql database create codeqldb --language=python --overwrite
for query in "${queries[@]}"; do
    codeql database analyze codeqldb --format=csv --output=query_results/$query.csv queries/$query.ql
done

cat query_results/*.csv
