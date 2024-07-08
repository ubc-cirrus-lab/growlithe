import os
import platform

###################################################################################################
system_platform = platform.system()
# Windows
if system_platform == 'Windows':
    growlithe_results_path = r"D:\Code\growlithe-results"

# MacOS
elif system_platform == 'Darwin':
    growlithe_results_path = "/Users/arshia/repos/ubc/final/growlithe-results"

# Linux
elif system_platform == 'Linux':
    growlithe_results_path = "/app/tasks/"
###################################################################################################

# ########## Benchmark1 #############
# benchmark_name = "Benchmark1"
# app_name = "ClaimProcessing"
# src_dir = "src"
# app_config_type = "SAM"
# app_config_path = ""
# ########## Benchmark1 #############
########## Benchmark2 #############
benchmark_name = "Benchmark2"
app_name = "ImageProcessing"
src_dir = "src"
app_config_type = "SAM"
app_config_path = os.path.join(growlithe_results_path, benchmark_name, app_name, "template.yaml")
########## Benchmark2 #############
########## Benchmark3 #############
# benchmark_name = "Benchmark3"
# app_name = "ShoppingCart"
# src_dir = "src"
# app_config_type = "StepFunction"
# app_config_path = ""
# ########## Benchmark3 #############

######## DO NOT CHANGE #############
benchmark_path = os.path.join(growlithe_results_path, benchmark_name)
app_path = os.path.join(benchmark_path, app_name)
src_path = os.path.join(app_path, src_dir)
new_app_path = os.path.join(benchmark_path, f"{app_name}Growlithe")
growlithe_path = os.path.join(benchmark_path, "Growlithe")
profiler_log_path = os.path.join(growlithe_path, "growlithe_profiler.log")
nodes_path = os.path.join(growlithe_path, "nodes.json")
policy_spec_path = os.path.join(growlithe_path, "policy_spec.json")