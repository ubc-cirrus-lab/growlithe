import os
import platform

###################################################################################################
system_platform = platform.system()
# Windows
if system_platform == 'Windows':
    growlithe_results_path = r"D:\Code\growlithe-results"

# MacOS
elif system_platform == 'Darwin':
    growlithe_results_path = "/Users/arshia/repos/growlithe-results"
    print("Operating system is macOS")
###################################################################################################

##### App Config

# App Path
app_path =  os.path.join(growlithe_results_path, "Benchmark-2", "claim-processing")
# Directory to store updated app, and intermediate growlithe files like codeql db, edge policies, etc.
app_growlithe_path = os.path.join(app_path, "..", "growlithe")


##### Codeql Config
codeql_db_path = os.path.join(app_growlithe_path, "codeqldb")
edge_policy_path = os.path.join(app_growlithe_path, "output", "edge_policies.json")

num_runs = 1
rerun_db_create = False
rerun_queries = True
queries_to_run = ["dataflows"]

# Growlithe Policy Config
regenerate_edge_policy = False
