from src.codeql.codeql import CodeQL
import os
from src.logger import logger

benchmarks_root_path = "D:\\Code\\serverless-compliance\\benchmarks"
# benchmark = "test"
benchmark = "ImageProcessingStateMachine"
benchmark_path = f'{benchmarks_root_path}\\{benchmark}\\'
codeql_db_path = f'{benchmarks_root_path}\\{benchmark}\\codeqldb\\'
codeql_output_path = f'{benchmarks_root_path}\\{benchmark}\\output\\'

queries = ['dataflows']
num_runs = 1
rerun = False

logger.info(f'Running {num_runs} CodeQL analyses on {benchmark}')
CodeQL.analyze(benchmark_path, queries, rerun=rerun, num_runs=num_runs)