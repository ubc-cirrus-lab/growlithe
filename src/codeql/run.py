from codeql import CodeQL
import os
from src.logger import logger
# from src.config import app_path, rerun_db_create, rerun_queries

queries = ['dataflows']
num_runs = 1
app_path = "D:\\Code\\growlithe-results\\Benchmark-1\\moderated-image-processing\\"
# app_path = "D:\\Code\\growlithe-results\\Benchmark-2\\claim-processing\\"
rerun_db_create = True
rerun_queries = True

logger.info(f'Running {num_runs} CodeQL analyses on {app_path}')
CodeQL.analyze(app_path, queries, rerun_db_create, rerun_queries, num_runs=num_runs)