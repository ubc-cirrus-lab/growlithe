import argparse
import step_function_helper
import sarif_extractor
import os
import node as Node

APP_NAME = "ImageProcessing"
QUERY_RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "output/")

def main(arn):
    graph = step_function_helper.handler_extractor(arn)
    print("Initial graph from configuration:")
    graph.print()

    # Iterate on a copy of the nodes as they are modified later
    functions = graph.nodes.copy()
    for node in functions:
        print("Extracting sources and sinks for ", node.name)
        sarif_extractor.add_internal_nodes(
            f"{QUERY_RESULTS_PATH}{APP_NAME}{node.name}_getSources.sarif",
            node, graph, Node.Node_Type.INTERNAL_SOURCE)
        sarif_extractor.add_internal_nodes(
            f"{QUERY_RESULTS_PATH}{APP_NAME}{node.name}_getSinks.sarif",
            node, graph, Node.Node_Type.INTERNAL_SINK)
        sarif_extractor.add_internal_edges(
            f"{QUERY_RESULTS_PATH}{APP_NAME}{node.name}_flowPaths.sarif", graph)

    graph.print()

    # FIXME: Update for new graph representation
    graph.visualize(vis_out_path=f"{QUERY_RESULTS_PATH}Graph.png", graphic=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("arn", help="State Machine ARN")
    args = parser.parse_args()
    main(args.arn)
