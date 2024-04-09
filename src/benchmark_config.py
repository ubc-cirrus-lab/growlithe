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
# app_path =  os.path.join(growlithe_results_path, "Benchmark-1", "moderated-image-processing")
# app_path =  os.path.join(growlithe_results_path, "Benchmark-2", "claim-processing")
app_path =  os.path.join(growlithe_results_path, "Benchmark-3", "shopping-cart")
# Directory to store updated app, and intermediate growlithe files like codeql db, edge policies, etc.
app_growlithe_path = os.path.join(app_path, "..", "growlithe")
app_growlithe_output_path = os.path.join(app_growlithe_path, "output")
profiler_log_path = os.path.join(app_growlithe_output_path, "growlithe_profiler.log")

##### Codeql Config
codeql_db_path = os.path.join(app_growlithe_path, "codeqldb")
num_runs = 1
rerun_db_create = True
rerun_queries = True
queries_to_run = ["dataflows"]

# Growlithe Policy Config
regenerate_edge_policy = False
edge_policy_path = os.path.join(app_growlithe_output_path, "edge_policies.json")
