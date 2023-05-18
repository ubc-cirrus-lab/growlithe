import boto3
import json
from graph import Graph
from node import Node_Type


def get_lambda_handler_name(arn):
    client = boto3.client("lambda")
    response = client.get_function(FunctionName=arn)
    return response["Configuration"]["Handler"]


def get_children(value):
    children = []
    if "Resource" in value and "lambda" in value["Resource"]:
        if value["Resource"] == "arn:aws:states:::lambda:invoke":
            handler = value["Parameters"]["FunctionName"]
        else:
            handler = value["Resource"]
    if "Next" in value:
        children.append(value["Next"])
    if "Choices" in value:
        for choice in value["Choices"]:
            children.append(choice["Next"])
    if "Catch" in value:
        for catch in value["Catch"]:
            children.append(catch["Next"])
    return handler, children


def handler_extractor(state_machine_arn):
    client = boto3.client("stepfunctions")
    response = client.describe_state_machine(stateMachineArn=state_machine_arn)
    states = json.loads(response["definition"])["States"]
    graph = extract_workflow(states)
    return graph


def extract_workflow(states):
    handlers = []
    graph = Graph()
    for key, value in states.items():
        if "Resource" in value and "lambda" in value["Resource"]:
            handler, children = get_children(value)
            handlers.append(f"{key}.{get_lambda_handler_name(handler)}.{children}")
            node = graph.find_node_or_create(key)
            node.type = Node_Type.FUNCTION
            for child in children:
                child_node = graph.find_node_or_create(child)
                child_node.type = Node_Type.FUNCTION
                node.add_child(child_node)
    return graph
