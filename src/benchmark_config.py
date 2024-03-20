import os

# app_path = "D:\\Code\\growlithe-results\\Benchmark-1\\moderated-image-processing"
# app_path = "D:\\Code\\growlithe-results\\Benchmark-2\\claim-processing"
app_path = "/Users/arshia/repos/growlithe-results/Benchmark-2/claim-processing"
# app_path = (
#     # "/Users/arshia/repos/growlithe-results/Benchmark-1/moderated-image-processing"
# )
app_growlithe_path = os.path.join(app_path, "..", "growlithe")

# Codeql Config
codeql_db_path = os.path.join(app_growlithe_path, "codeqldb")
edge_policy_path = os.path.join(app_growlithe_path, "output", "edge_policies.json")
regenerate_edge_policy = True
