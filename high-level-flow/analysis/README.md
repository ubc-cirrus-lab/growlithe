# High-level Analysis Guide

- `run-analysis.sh`: This script will do a high-level dataflow analysis on a deployed step function. To run the script you need to pass the ARN of the step function as an argument:
    ``` bash
    run-analysis.sh <STEP_FUNCTION_ARN>
    ```
- `step-functions.py`: This script extracts the handler functions from a step function's definition and creates a graph representing workflow.
- `run-queries.sh`: Run this script to create the CodeQL database and collect the query results. (__Not used anymore__)
- `queries.py`: This script reads the query results and generates a graph of the function's external interactions. (__Not used anymore__)