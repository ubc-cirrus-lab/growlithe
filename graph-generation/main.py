import argparse
import step_function_helper
import sarif_extractor
import os
from node import DataflowType

APP_NAME = "ImageProcessing"
QUERY_RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "output/")


def main(arn):
    # =================================== Build Dependency Graph ========================================== #
    # Stage 1: Extract functions from state machine
    graph = step_function_helper.handler_extractor(arn)
    print("Initial graph from configuration:")
    # graph.print()

    # Iterate on a copy of the nodes as they are modified later
    functions = graph.nodes.copy()

    # Stage 2, 3: Extract sources and sinks within each function from SARIF files & add internal edges
    for node in functions:
        print("Expanding internal graph for ", node.name)
        sarif_extractor.add_internal_nodes(
            f"{QUERY_RESULTS_PATH}{APP_NAME}{node.name}_getSources.sarif",
            node, graph, DataflowType.SOURCE)
        sarif_extractor.add_internal_nodes(
            f"{QUERY_RESULTS_PATH}{APP_NAME}{node.name}_getSinks.sarif",
            node, graph, DataflowType.SINK)
        sarif_extractor.add_internal_edges(
            f"{QUERY_RESULTS_PATH}{APP_NAME}{node.name}_flowPaths.sarif", graph)

    # Stage 4: Connect internal nodes to external nodes
    # TODO: Refactor for other kinds of invocations
    graph.connect_nodes_across_functions(graph.nodes[0])

    print("Graph after adding internal nodes and edges:")
    # graph.print()

    # =================================== Policy Initialization ========================================== #
    # Stage 5: Suggest direct policies to developer
    graph.init_policies()
    print("Suggested policies")
    # TODO: Allow devs to update and modify selected policies

    # =================================== Taint Set Generation ========================================== #
    graph.generate_taints()
    # =================================== Edge Annotation (Static Enforcement) ===================================== #
    graph.annotate_edges()
    # graph.init_security_labels(f"{QUERY_RESULTS_PATH}{APP_NAME}_security_labels.json")
    # graph.find_violations()

    print("Final graph:")

    # FIXME: Update for new graph representation
    # graph.visualize(vis_out_path=f"{QUERY_RESULTS_PATH}Graph.png", graphic=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("arn", help="State Machine ARN")
    args = parser.parse_args()
    main(args.arn)
