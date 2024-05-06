import ast
import json
import os
import shutil
import time
from sarif import loader
from src.iam_generator.iam_generator import IAMGenerator
from src.logger import logger, profiler_logger
from src.taint_tracker.taint_tracker import TaintTracker
from src.graph.graph import Graph, InterfaceType, Edge
from src.graph.parser import parse_and_add_flow
from src.graph.policy.policy import Policy, EdgePolicy
from src.graph.utils import *
from collections import defaultdict
from src.benchmark_config import *

results = []
for language in ["python", "javascript"]:
    sarif_data = loader.load_sarif_file(
        os.path.join(app_growlithe_path, "output", f"dataflows_{language}.sarif")
    )
    results.extend(sarif_data.get_results())

for i in range(num_runs):
    profiler_logger.info(
        "=========================================================================="
    )
    profiler_logger.info(
        f"Running iteration {i+1}/{num_runs} of Graph analysis & instrumentation..."
    )

    #########################################################
    # Generate the graph structure
    start_time = time.time()
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

    profiler_logger.info(
        f"Graph generation completed in {time.time() - start_time} seconds"
    )

    # Temporary variable to debug intra-function graph
    # TODO: Integrate stitcher again and remove selection for smaller part
    # graph = graph.get_sub_graph(
    #     "transform_image.py"
    # )
    logger.info("Generated Graph Successfully and stored default policies")

    #########################################################
    # Generate initial policies for the graph
    if regenerate_edge_policy:
        logger.warning("=== Regenerating policy ===")
        start_time = time.time()
        graph.init_policies(edge_policy_path)
        profiler_logger.info(
            f"Policy generation completed in {time.time() - start_time} seconds"
        )
    else:
        logger.warning("=== Using previously generated policy ===")
        graph.append_policies(edge_policy_path)
    #########################################################

    # Load edge policies from json containing policy predicates as strings
    edge_policies = json.load(open(edge_policy_path))
    edge_policies = [EdgePolicy(policy) for policy in edge_policies]
    edge_policy_map = {}

    for policy in edge_policies:
        edge_policy_map[
            (policy.source_function, policy.source, policy.sink_function, policy.sink)
        ] = policy

    start_time = time.time()
    tainted_file_trees = TaintTracker(graph).run()

    #########################################################
    # Go through all edges and assign edge policies
    graph.apply_edges(
        taint_generation_and_policy_instrumentation, edge_policy_map, tainted_file_trees
    )

    #########################################################
    # Add required import statements
    if tainted_file_trees is not None:
        for tree in tainted_file_trees.values():
            tree.body.insert(
                0,
                ast.ImportFrom(
                    module="growlithe_predicates",
                    names=[ast.alias(name="*", asname=None)],
                ),
            )

        # Write the tainted trees to the file system
        for file, tree in tainted_file_trees.items():
            directory = os.path.split(f"{app_growlithe_path}/{file}")[0]
            os.makedirs(directory, exist_ok=True)
            shutil.copy(
                f'{os.path.join(os.path.dirname(os.path.abspath(__file__)),"policy/policy_predicates.py")}',
                os.path.join(directory, "growlithe_predicates.py"),
            )
            with open(os.path.join(app_growlithe_path, file), "w") as f:
                f.write(ast.unparse(ast.fix_missing_locations(tree)))

    profiler_logger.info(
        f"Policy Instrumentation completed in {time.time() - start_time} seconds"
    )
    #########################################################
    # Generate IAM policies
    start_time = time.time()

    IAMGenerator(graph).run()
    profiler_logger.info(
        f"IAM Generation completed in {time.time() - start_time} seconds"
    )
