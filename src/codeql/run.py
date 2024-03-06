from codeql import CodeQL
import os
from src.logger import logger
# from src.config import app_path, rerun_db_create, rerun_queries

queries = ['dataflows']
num_runs = 1
app_path = "D:\\Code\\growlithe\\benchmarks\\monitored-image-processing"
rerun_db_create = False
rerun_queries = True

logger.info(f'Running {num_runs} CodeQL analyses on {app_path}')
CodeQL.analyze(app_path, queries, rerun_db_create, rerun_queries, num_runs=num_runs)