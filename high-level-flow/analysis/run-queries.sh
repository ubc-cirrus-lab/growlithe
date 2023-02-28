#! /bin/bash

set -ex
queries=(file requests socket boto3)
cd ../code
mkdir -p query_results
codeql database create codeqldb --language=python --overwrite
for query in "${queries[@]}"; do
    codeql database analyze codeqldb --format=csv --output=query_results/$query.csv queries/$query.ql
done
