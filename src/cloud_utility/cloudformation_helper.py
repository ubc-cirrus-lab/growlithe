import json
import yaml

from src.graph.node import NodeType
from src.graph.graph import Graph
from src.logger import logger


def handler_extractor(template_path):
    if template_path.endswith(".yaml") or template_path.endswith(".yml"):
        resources = yaml.load(open(template_path, "r").read(), Loader=yaml.FullLoader)["Resources"]
    elif template_path.endswith(".json"):
        resources = json.loads(open(template_path, "r").read())["Resources"]
    else:
        logger.critical("Template file's extension is not valid. Supported extensions: yaml, yml, json")
        exit(1)
    graph = extract_workflow(resources)
    return graph


def extract_workflow(resources):
    graph = Graph()
    for key, value in resources.items():
        type = value.get('Type')
        if type == 'AWS::Serverless::Function':
            node_name = value['Properties']['Handler'].split('.')[0]
            lambda_node = graph.find_node_or_create(node_name)
            lambda_node.node_type = NodeType.FUNCTION
            if 'Events' in value['Properties']:
                for event in value['Properties']['Events'].values():
                    if event['Type'] == 'DynamoDB':
                        db_name = event['Properties']['Stream']['Fn::GetAtt'][0]
                        db_node = graph.find_node_or_create(
                            db_name if 'TableName' not in resources[db_name]['Properties'] else
                            resources[db_name]['Properties']['TableName'])
                        lambda_node.node_type = NodeType.FUNCTION
                        db_node.add_edge(lambda_node)
        elif type == 'AWS::DynamoDB::Table':
            db_name = key if 'TableName' not in value['Properties'] else value['Properties']['TableName']
            db_node = graph.find_node_or_create(db_name)
            db_node.node_type = NodeType.DYNAMODB_TABLE
    return graph
