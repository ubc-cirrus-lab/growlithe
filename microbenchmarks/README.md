## Microbenchmarks

- **Linear Chain**: Runs n functions sequentially in a linear chain
- **Fanout**: Runs n functions in parallel

### Usage
- Use `generate_app.py` with required configuration to generate and deploy application with n lambda functions.
The same lambda functions will be used for both linear chain and fanout.
- Run Growlithe using `run_growlithe.py`. This also profiles and gets the time taken.
- Deploy runner functions in `runners/` directory
- Configure and run `run_microbenchmark.py` to run linear_chain and fanout workloads.
- For each of them, generate required statistics by running `analyze.py` and `plot.py`