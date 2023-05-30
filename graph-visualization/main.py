import argparse
import step_function_helper
import sarif_extractor
import os
from node import Node_Type

APP_NAME = "ImageProcessing"
QUERY_RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "output/")

def main(arn):
    # Stage 1: Extract functions from state machine
    graph = step_function_helper.handler_extractor(arn)
    print("Initial graph from configuration:")
    graph.print()

    # Iterate on a copy of the nodes as they are modified later
    functions = graph.nodes.copy()

    # Stage 2, 3: Extract sources and sinks within each function from SARIF files & add internal edges
    for node in functions:
        print("Extracting sources and sinks for ", node.name)
        sarif_extractor.add_internal_nodes(
            f"{QUERY_RESULTS_PATH}{APP_NAME}{node.name}_getSources.sarif",
            node, graph, Node_Type.INTERNAL_SOURCE)
        sarif_extractor.add_internal_nodes(
            f"{QUERY_RESULTS_PATH}{APP_NAME}{node.name}_getSinks.sarif",
            node, graph, Node_Type.INTERNAL_SINK)
        sarif_extractor.add_internal_edges(
            f"{QUERY_RESULTS_PATH}{APP_NAME}{node.name}_flowPaths.sarif", graph)

    # Stage 4: Connect internal nodes to external nodes
    # TODO: Refactor for other kinds of invocations
    graph.connect_nodes_across_functions()

    print("Graph after adding internal nodes and edges:")
    graph.print()
    
    # Stage 5: Annotate nodes with security labels and propagate them
    graph.init_security_labels(f"{QUERY_RESULTS_PATH}{APP_NAME}_security_labels.json")
    graph.traverse_propagate_labels()
    # FIXME: Update for new graph representation
    graph.visualize(vis_out_path=f"{QUERY_RESULTS_PATH}Graph.png", graphic=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("arn", help="State Machine ARN")
    args = parser.parse_args()
    main(args.arn)
