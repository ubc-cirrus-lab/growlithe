import argparse
import step_function_helper
import utility
import boto3_helper

APP_NAME = "ImageProcessing"
QUERY_RESULTS_PATH = "../output/"


def main(arn):
    graph = step_function_helper.handler_extractor(arn)
    
    # get a copy of the nodes as they are changing in the extend graph method
    functions = graph.nodes.copy()
    for node in functions:
        result = utility.get_query_results(
            f"{QUERY_RESULTS_PATH}{APP_NAME}{node.name}.sarif"
        )
        if len(result) > 0:
            boto3_helper.extend_graph(result[0], node, graph)

    graph.visualize(graphic=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("arn", help="State Machine ARN")
    args = parser.parse_args()
    main(args.arn)
