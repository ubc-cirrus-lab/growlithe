#!/bin/bash

set -ex

wget https://github.com/github/codeql-cli-binaries/releases/download/v2.12.3/codeql-linux64.zip
unzip codeql-linux64.zip > /dev/null 2>&1
PATH=$PATH:$(pwd)/codeql
export PATH
