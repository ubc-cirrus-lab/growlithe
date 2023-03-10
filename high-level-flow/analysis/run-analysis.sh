#!/bin/bash

set -ex

HANDLER_FILE=handlers.csv
RESULTS_FILE=query-results.sarif
STEP_FUNCTION_ARN=arn:aws:states:us-east-1:880306299867:stateMachine:ImageProcessing

mkdir -p tmp/src
cp linker.py step_functions.py sarif_parser.py tmp/
cp -r ../../benchmarks/ImageProcessingStateMachine/* tmp/src/
mkdir -p tmp/query_templates
cp ../code/queries/* tmp/query_templates/
cp ../code/qlpack.yml tmp/
cd tmp

# Get handler functions
python3 step_functions.py $STEP_FUNCTION_ARN -o $HANDLER_FILE

# Create function-specific queries
mkdir ./queries
python3 linker.py $HANDLER_FILE

# Run queries
cd src
codeql database create codeqldb --language=python --overwrite
cd ..
codeql pack install
codeql database analyze ./src/codeqldb ./queries/ --format=sarifv2.1.0 --output=$RESULTS_FILE

# Parse results
python3 sarif_parser.py $RESULTS_FILE $HANDLER_FILE

cd ..
rm -r tmp