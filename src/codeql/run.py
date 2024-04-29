from codeql import CodeQL
from src import benchmark_config
from src.logger import logger


logger.info(
    f"Running {benchmark_config.num_runs} CodeQL analyses on {benchmark_config.app_path}"
)
for language in benchmark_config.languages:
    CodeQL.analyze(
        benchmark_config.app_path,
        benchmark_config.queries_to_run,
        benchmark_config.rerun_db_create,
        benchmark_config.rerun_queries,
        language,
        benchmark_config.num_runs,
    )
