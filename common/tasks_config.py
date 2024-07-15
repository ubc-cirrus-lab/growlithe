"""
Defines tasks in growlithe to be run or skipped on the app
Also defines number of runs
"""

CREATE_CODEQL_DB = False
RUN_CODEQL_QUERIES = False
GENERATE_EDGE_POLICY = False
PROFILE_GROWLITHE_RUNS = True

HYBRID_MODE = True
CONSOLE_LOG_LEVEL = "DEBUG"
FILE_LOG_LEVEL = "INFO"

codeql_queries = ["dataflows", "metadataflows"]

