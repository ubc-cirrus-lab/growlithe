from src.logger import logger
from src.graph.graph import Graph, Edge, Node, ReferenceType
from src.benchmark_config import app_growlithe_path

import json

ACCOUNT_ID = "880306299867"  # TODO: get from config
REGION = "us-east-1"  # TODO: get from config


class IAMGenerator:
    def __init__(self, graph: Graph):
        self.edges: list[Edge] = graph.edges
        self.function_roles: dict[str, dict] = {}

    def run(self):
        logger.info("Running IAM Generator")
        logger.info("Generating roles for lambda functions")
        self.initialize_function_roles()
        self.generate_function_roles()
        self.save_roles()

    def save_roles(self):
        for function, role in self.function_roles.items():
            try:
                with open(
                    f"{app_growlithe_path}/LambdaFunctions/{function}/role.json", "w"
                ) as f:
                    json.dump(role, f, indent=4)
            except FileNotFoundError:
                logger.warning(
                    f"Function {function} does not have a directory in {app_growlithe_path}/LambdaFunctions"
                )

    def initialize_function_roles(self):
        for edge in self.edges:
            source_node: Node = edge.source_node
            sink_node: Node = edge.sink_node
            try:
                source_function: str = source_node.function.split("/")[
                    1
                ]  # TODO: define a field for raw function name
                sink_function: str = sink_node.function.split("/")[
                    1
                ]  # TODO: define a field for raw function name
            except IndexError:
                source_function = source_node.function
                sink_function = sink_node.function
            if source_function not in self.function_roles.keys():
                self.function_roles[source_function] = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "logs:CreateLogGroup",
                            "Resource": f"arn:aws:logs:{REGION}:{ACCOUNT_ID}:*",
                        }
                    ],
                }
                log_statement = {
                    "Effect": "Allow",
                    "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
                    "Resource": [
                        f"arn:aws:logs:{REGION}:{ACCOUNT_ID}:log-group:/aws/lambda/{source_function}:*"
                    ],
                }
                self.function_roles[source_function]["Statement"].append(log_statement)
            if sink_function not in self.function_roles.keys():
                self.function_roles[sink_function] = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "logs:CreateLogGroup",
                            "Resource": f"arn:aws:logs:{REGION}:{ACCOUNT_ID}:*",
                        }
                    ],
                }
                log_statement = {
                    "Effect": "Allow",
                    "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
                    "Resource": [
                        f"arn:aws:logs:{REGION}:{ACCOUNT_ID}:log-group:/aws/lambda/{sink_function}:*"
                    ],
                }
                self.function_roles[sink_function]["Statement"].append(log_statement)

    def generate_function_roles(self):
        for edge in self.edges:
            source_node: Node = edge.source_node
            sink_node: Node = edge.sink_node
            try:
                source_function: str = source_node.function.split("/")[
                    1
                ]  # TODO: define a field for raw function name
                sink_function: str = sink_node.function.split("/")[
                    1
                ]  # TODO: define a field for raw function name
            except IndexError:
                source_function = source_node.function
                sink_function = sink_node.function
            if sink_node.resource_type == "S3_BUCKET":
                logger.info(f"Generating role for {sink_function}")
                object_name = "*"
                if sink_node.data_object.reference_type == ReferenceType.STATIC:
                    object_name = sink_node.data_object.reference_name
                s3_statement = {
                    "Effect": "Allow",
                    "Action": ["s3:PutObject"],
                    "Resource": f"arn:aws:s3:::{sink_node.resource_name.reference_name}/{object_name}",
                }
                self.function_roles[source_function]["Statement"].append(s3_statement)
            if source_node.resource_type == "S3_BUCKET":
                logger.info(f"Generating role for {source_function}")
                object_name = "*"
                if source_node.data_object.reference_type == ReferenceType.STATIC:
                    object_name = source_node.data_object.reference_name
                s3_statement = {
                    "Effect": "Allow",
                    "Action": ["s3:GetObject"],
                    "Resource": f"arn:aws:s3:::{source_node.resource_name.reference_name}/{object_name}",
                }
                self.function_roles[sink_function]["Statement"].append(s3_statement)
        logger.info("IAM generation complete")
