"""
Defines tasks in growlithe to be run or skipped on the app
Also defines number of runs
"""

CREATE_CODEQL_DB = True
RUN_CODEQL_QUERIES = True
GENERATE_EDGE_POLICY = True
PROFILE_GROWLITHE_RUNS = True

HYBRID_ENFORCEMENT_MODE = True
CONSOLE_LOG_LEVEL = "DEBUG"
FILE_LOG_LEVEL = "INFO"

codeql_queries = ["dataflows", "metadataflows"]
