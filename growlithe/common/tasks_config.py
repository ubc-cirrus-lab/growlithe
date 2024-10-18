"""
Configuration module for Growlithe tasks and runtime settings.

This module defines various configuration flags and settings that control
the behavior of Growlithe during its execution. It specifies which tasks
should be run, logging levels, and other operational parameters.

Useful knobs to configure during development or debugging.
"""

# Flag to control creation of CodeQL database
CREATE_CODEQL_DB = True

# Flag to control execution of CodeQL queries
RUN_CODEQL_QUERIES = True

# Flag to control generation of edge policies
GENERATE_EDGE_POLICY = True

# Flag to enable profiling of Growlithe runs
PROFILE_GROWLITHE_RUNS = True

# Flag to enable hybrid enforcement mode
HYBRID_ENFORCEMENT_MODE = True

# Logging level for console output
CONSOLE_LOG_LEVEL = "DEBUG"

# Logging level for file output
FILE_LOG_LEVEL = "INFO"

# List of CodeQL queries to be executed
codeql_queries = ["dataflows", "metadataflows"]
