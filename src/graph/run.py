from sarif import loader
from src.logger import logger
from src.graph.graph import Graph, InterfaceType, Edge
from src.graph.parser import parse_and_add_flow
from src.graph.policy.policy import Policy, EdgePolicy
from src.graph.policy.policy_evaluator import try_policy_eval
import json
from collections import defaultdict

# TODO: Move to config and make paths os independent
benchmarks_root_path = "D:\\Code\\serverless-compliance\\benchmarks"
benchmark = "ImageProcessingStateMachine"
codeql_db_path = f"{benchmarks_root_path}\\{benchmark}\\codeqldb\\"
codeql_output_path = f"{benchmarks_root_path}\\{benchmark}\\output\\"

sarif_data = loader.load_sarif_file(f"{codeql_output_path}\\dataflows.sarif")
results = sarif_data.get_results()

# Generate the graph structure
graph = Graph()
for result in results:
    related_locations = result["relatedLocations"]
    for flow in result["message"]["text"].split("\n"):
        # Flows are typically in form of"[SOURCE, GLOBAL, S3_BUCKET:STATIC:imageprocessingbenchmark, STATIC:sample_2.png](1)==>[SINK, CONTAINER, LOCAL_FILE:STATIC:tempfs, DYNAMIC:tempFile](2)"
        parse_and_add_flow(
            flow,
            graph,
            related_locations,
            default_function=result["locations"][0]["physicalLocation"][
                "artifactLocation"
            ]["uri"],
        )

# Temporary variable to debug intra-function graph
# TODO: Integrate stitcher again and remove selection for smaller part
graph = graph.get_sub_graph(
    "LambdaFunctions/ImageProcessingRotate/lambda_function.py"
)

logger.info("Generated Graph Successfully")

# An example of a dev-specified policy
# str_policies = [
#     # Policy that can be resolved statically
#     "RESOURCE:S3_BUCKET:imageprocessingbenchmark => FUNCTION:LambdaFunctions/ImageProcessingRotate/lambda_function.py ? isSuffix(PropDataObjectName, '.jpg')",
#     # Policy that requires run time checks
#     # "FUNCTION:LambdaFunctions/ImageProcessingRotate/lambda_function.py => RESOURCE:S3_BUCKET:imageprocessingbenchmark ? gt(SessionTime, 1704810019) & lt(SessionTime, 1707810019)",

#     "FUNCTION:LambdaFunctions/ImageProcessingRotate/lambda_function.py => RESOURCE:S3_BUCKET:imageprocessingbenchmark ? taintSetContains('RESOURCE:S3_BUCKET:imageprocessingbenchmark')",

#     # "FUNCTION:LambdaFunctions/ImageProcessingRotate/lambda_function.py => LOCAL_FILE:tempfs ? isVar(PropDataObjectName)",
#     # "FUNCTION:LambdaFunctions/ImageProcessingRotate/lambda_function.py => LOCAL_FILE:tempfs ? isVar(PropDataObjectName)",
# ]

# policies = [Policy(policy) for policy in str_policies]

# Load edge policies from json containing policy predicates as strings
edge_policies = json.load(open(f"{codeql_output_path}\\edge_policies.json"))
edge_policies = [EdgePolicy(policy) for policy in edge_policies]
# Create a map of from, to to edge policy
edge_policy_map = {}
source_instrumentation_map = defaultdict(set)
for policy in edge_policies:
    edge_policy_map[(policy.start, policy.end)] = policy

def update_instrumentation_map(codePath, eval_results):
    if (eval_results == True):
            pass
    elif (eval_results == False):
        # TODO: Collect all errors for developers to see separately
        pass
    else:
        logger.info("TODO: Add to source code")
        logger.info("=================================")
        logger.info(eval_results)
        logger.info("=================================")

        # source_instrumentation_map[codePath] += eval_results
        # TODO: Either add to source code or collect and add all assertions relevant to the
        # read/write together

def assign_policy(edge: Edge):
    from_to_policy_key = (edge.source_node.policy_id(), edge.sink_node.policy_id())

    if from_to_policy_key in edge_policy_map:
        edge.edge_policy = edge_policy_map[from_to_policy_key]
        read_pol_eval = try_policy_eval(edge.edge_policy.read_policy, edge.source_node)
        update_instrumentation_map(edge.source_properties['CodePath'], read_pol_eval)
        write_pol_eval = try_policy_eval(edge.edge_policy.write_policy, edge.sink_node)
        update_instrumentation_map(edge.sink_properties['CodePath'], write_pol_eval)
    else:
        # TODO: This should be an error as we expect all edges to have a policy in the json
        # logger.warn(f"No policy found for edge {edge.source_node} -> {edge.sink_node}")
        pass

# Go through all edges and assign edge policies
graph.apply_edges(assign_policy)

# Insert required imports in lambda functions
# TODO: Ensure that policy_predicates is in the same directory, or update statement according to relative path

for function in graph.functions:
    imports = ['from pyDatalog import pyDatalog', 'from policy_predicates import *']

# # For each node in the graph, check if it matches any policy
# for node in graph.nodes:
#     node_function = f"FUNCTION:{node.function}"

#     # How should it be represented for a dynamic one?
#     node_resource = f"RESOURCE:{node.resource_type}:{node.resource_name.reference_name}"
#     # print('Node Resource is ', node_resource)
#     for policy in policies:
#         if node_function == policy.start and node_resource == policy.end and node.interface_type == InterfaceType.SINK:
#             logger.info(f"Found write policy {policy.rhs}")
#             evaluate_policy(policy.rhs, node, "")

#         elif node_resource == policy.start and node_function == policy.end and node.interface_type == InterfaceType.SOURCE:
#             logger.info(f"Found read policy {policy.rhs}")
#             evaluate_policy(policy.rhs, node, "")

