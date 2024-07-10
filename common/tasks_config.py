"""
Defines tasks in growlithe to be run or skipped on the app
Also defines number of runs
"""

CREATE_CODEQL_DB = True
RUN_CODEQL_QUERIES = True
GENERATE_EDGE_POLICY = True
PROFILE_GROWLITHE_RUNS = True

# # Directory to store updated app, and intermediate growlithe files like codeql db, edge policies, etc.
# app_growlithe_path = os.path.join(app_path, "..", "growlithe")
# app_growlithe_output_path = os.path.join(app_growlithe_path, "output")

# ##### Codeql Config
# # codeql_db_path = os.path.join(app_growlithe_path, "codeqldb")
# num_runs = 1
# rerun_db_create = False
# rerun_queries = True

codeql_queries = ["dataflows", "metadataflows"]

# # Growlithe Policy Config
# regenerate_edge_policy = True
# edge_policy_path = os.path.join(app_growlithe_output_path, "edge_policies.json")
