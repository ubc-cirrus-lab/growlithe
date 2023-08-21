import boto3
import json
import os
from graph import Graph
from node import NodeType


def get_lambda_handler_name(arn):
    return "lambda_handler"
    # client = boto3.client("lambda")
    # response = client.get_function(FunctionName=arn)
    # return response["Configuration"]["Handler"]


def get_edges(value):
    edges = []
    handler = None
    if "Resource" in value and "lambda" in value["Resource"]:
        if value["Resource"] == "arn:aws:states:::lambda:invoke":
            handler = value["Parameters"]["FunctionName"]
        else:
            handler = value["Resource"]
    if "Next" in value:
        edges.append(value["Next"])
    if "Choices" in value:
        for choice in value["Choices"]:
            edges.append(choice["Next"])
    if "Catch" in value:
        for catch in value["Catch"]:
            edges.append(catch["Next"])
    return handler, edges


def handler_extractor(state_machine_arn, APP_SRC_PATH):
    print("Extracting handlers from state machine ", state_machine_arn)
    if os.path.isfile(state_machine_arn):
        states = json.loads(open(state_machine_arn, "r").read())["States"]
    else:
        client = boto3.client("stepfunctions")
        response = client.describe_state_machine(stateMachineArn=state_machine_arn)
        states = json.loads(response["definition"])["States"]
    graph = extract_workflow(states, APP_SRC_PATH)
    return graph


def extract_workflow(states, APP_SRC_PATH):
    handlers = []
    graph = Graph()
    for key, value in states.items():
        # Search for lambda functions in the state machine
        if "Resource" in value and "lambda" in value["Resource"]:
            handler, edges = get_edges(value)
            handlers.append(f"{key}.{get_lambda_handler_name(handler)}.{edges}")

            # FIXME: Update to ensure unique ids instead of just names
            node = graph.find_node_or_create(key)
            node.nodeType = NodeType.FUNCTION
            node.file_path = f"{APP_SRC_PATH}/{key}.py"
            for edge in edges:
                edgeNode = graph.find_node_or_create(edge)
                edgeNode.type = NodeType.FUNCTION
                edgeNode.file_path = f"{APP_SRC_PATH}/{edge}.py"
                node.add_edge(edgeNode)
    return graph
