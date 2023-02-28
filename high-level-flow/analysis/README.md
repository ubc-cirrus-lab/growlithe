# High-level Analysis Guide

- `run-queries.sh`: Run this script to create the CodeQL database and collect the query results.
- `step-functions.py`: This script extracts the handler functions from a step function's definition and creates a graph of the workflow.
- `queries.py`: This script reads the query results and generates a graph of the function's external interactions.