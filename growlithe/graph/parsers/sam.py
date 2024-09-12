"""
Parses an AWS SAM template file to give a list of resource and their properties like events
"""

import os
import json
import shutil
import yaml
import ast

from typing import List
from cfn_flip import load_yaml, yaml_dumper
from growlithe.common.file_utils import get_file_extension
from growlithe.common.utils import profiler_decorator
from growlithe.config import Config
from growlithe.graph.adg.graph import Graph
from growlithe.graph.adg.node import Node
from growlithe.graph.adg.resource import Resource, ResourceType
from growlithe.graph.adg.function import Function
from growlithe.common.logger import logger
from growlithe.graph.adg.types import Scope


class SAMParser:
    def __init__(self, sam_file, config):
        self.sam_file: str = sam_file
        self.config: Config = config
        self.parsed_yaml = None
        self.step_function_path = None
        self.resources: List[Resource] = self.parse_sam_template()

    def parse_state_machine(
        self, definition_path: str, step_function: Resource, resources: List[Resource]
    ):
        substitutions = {}
        if "DefinitionSubstitutions" in step_function.metadata.keys():
            for key, value in step_function.metadata["DefinitionSubstitutions"].items():
                substitutions[key] = (
                    value.items()[0][1][0]
                    if value.items()[0][0] == "Fn::GetAtt"
                    else value
                )

        with open(definition_path, "r") as f:
            states = json.loads(f.read())
        self.fix_dependencies(
            step_function=step_function,
            resources=resources,
            substitutions=substitutions,
            states=states,
        )
        for _, state in states["States"].items():
            # get source function
            self.extract_dependencies(
                resources=resources,
                substitutions=substitutions,
                states=states,
                state=state,
            )

    def extract_dependencies(self, resources, substitutions, states, state):
        source_function = None
        if state["Type"] == "Task":
            source_function_name = state["Parameters"]["FunctionName"]
            if "$" in source_function_name:
                source_function_name = substitutions[source_function_name[2:-1]]
            source_function = self.find_resource(source_function_name, resources)

        if source_function and "Next" in state.keys():
            next_state = states["States"][state["Next"]]
            if next_state["Type"] == "Task":
                target_function_name = next_state["Parameters"]["FunctionName"]
                if "$" in target_function_name:
                    target_function_name = substitutions[target_function_name[2:-1]]
                target_function = self.find_resource(target_function_name, resources)
                source_function.add_dependency(target_function)
            elif next_state["Type"] == "Choice":
                for choice in next_state["Choices"]:
                    target = choice["Next"]
                    default = next_state["Default"]
                    target_function_name = states["States"][target]["Parameters"][
                        "FunctionName"
                    ]
                    default_function_name = states["States"][default]["Parameters"][
                        "FunctionName"
                    ]
                    if "$" in target_function_name:
                        target_function_name = substitutions[target_function_name[2:-1]]
                    if "$" in default_function_name:
                        default_function_name = substitutions[
                            default_function_name[2:-1]
                        ]
                    target_function = self.find_resource(
                        target_function_name, resources
                    )
                    default_function = self.find_resource(
                        default_function_name, resources
                    )
                    source_function.add_dependency(target_function)
                    source_function.add_dependency(default_function)
            elif next_state["Type"] == "Catch":
                target = next_state["Next"]
                target_function_name = states["States"][target]["Parameters"][
                    "FunctionName"
                ]
                if "$" in target_function_name:
                    target_function_name = substitutions[target_function_name[2:-1]]
                target_function = self.find_resource(target_function_name, resources)
                source_function.add_dependency(target_function)
            else:
                logger.error(f"Unsupported state type: {next_state['Type']}")
                raise NotImplementedError

    def fix_dependencies(self, step_function, resources, substitutions, states):
        start_state = states["States"][states["StartAt"]]
        function_name = start_state["Parameters"]["FunctionName"]
        if "$" in function_name:
            function_name = substitutions[function_name[2:-1]]

        # fix dependencies: remove step function and add the first function
        step_function_parents = []
        for resource in resources:
            if step_function in resource.dependencies:
                step_function_parents.append(resource)
        for parent in step_function_parents:
            parent.dependencies.remove(step_function)
            function = self.find_resource(function_name, resources)
            parent.dependencies.append(function)
            function.metadata = step_function.metadata

    @profiler_decorator
    def parse_sam_template(self):
        resources: List[Resource] = []
        has_step_function = False
        with open(self.sam_file, "r") as f:
            self.parsed_yaml = load_yaml(f.read())
        for resource_name, resource_details in self.parsed_yaml["Resources"].items():
            if resource_details["Type"] == "AWS::Serverless::Function":
                code_uri = resource_details["Properties"]["CodeUri"]
                handler = resource_details["Properties"]["Handler"]
                runtime = resource_details["Properties"]["Runtime"]
                handler_path = handler.split(".")[0]
                file_extension = get_file_extension(runtime)

                # Construct the full path to the Lambda function's code
                function_path = os.path.normpath(
                    os.path.join(
                        self.config.benchmark_path,
                        code_uri,
                        f"{handler_path}{file_extension}",
                    )
                )
                growlithe_function_path = os.path.normpath(
                    os.path.join(
                        self.config.growlithe_path,
                        code_uri,
                        f"{handler_path}{file_extension}",
                    )
                )
                resource = Function(
                    name=resource_name,
                    type=ResourceType(resource_details["Type"]),
                    runtime=resource_details["Properties"]["Runtime"],
                    function_path=function_path,
                    growlithe_function_path=growlithe_function_path,
                    metadata=resource_details["Properties"],
                )
            else:
                try:
                    resource: Resource = Resource(
                        name=resource_name,
                        type=ResourceType(resource_details["Type"]),
                        metadata=resource_details["Properties"],
                    )
                except ValueError:
                    logger.warning(
                        "Unsupported resource type: %s", resource_details["Type"]
                    )
            if resource_details["Type"] == "AWS::Serverless::StateMachine":
                definition_uri: str = os.path.join(
                    *resource_details["Properties"]["DefinitionUri"].split(os.sep)
                )
                sam_file_dir: str = os.path.dirname(self.sam_file)
                definition_path: str = os.path.join(sam_file_dir, definition_uri)
                self.step_function_path = definition_path
                has_step_function: bool = True
                parent_step_function: Resource = resource
            resources.append(resource)

        # extract dependencies
        for resource in resources:
            if "Events" in resource.metadata.keys():
                events: dict = resource.metadata["Events"].values()
                for event in events:
                    event_type: str = event["Type"]
                    properties: dict = event["Properties"]
                    ref: List[str] = []
                    if event_type == "Api":
                        ref.append(properties["RestApiId"]["Ref"])
                    elif event_type == "DynamoDB":
                        ref.append(properties["Stream"]["Fn::GetAtt"][0])
                    elif event_type == "EventBridgeRule":
                        ref.extend(
                            bucket["Ref"]
                            for bucket in properties["Pattern"]["detail"]["bucket"][
                                "name"
                            ]
                        )
                    source_resource: Resource = None
                    for ref in ref:
                        source_resource = self.find_resource(
                            ref=ref, resources=resources
                        )
                        source_resource.add_dependency(resource)
        if has_step_function:
            self.parse_state_machine(
                definition_path=definition_path,
                step_function=parent_step_function,
                resources=resources,
            )
        return resources

    def find_resource(self, ref, resources):
        for res in resources:
            if ref == res.name:
                return res

    def get_functions(self) -> List[Function]:
        return [
            resource for resource in self.resources if isinstance(resource, Function)
        ]

    def get_resources(self) -> List[Resource]:
        return self.resources

    def modify_config(self, graph: Graph):
        self.fix_function_names()
        self.add_lambda_layer()
        self.add_iam_roles(graph)
        self.add_resource_policies(graph)

    def fix_function_names(self):
        """
        Fixes the function names for AWS::Serverless::Function resources in the parsed YAML.

        Iterates through each resource in the parsed YAML and checks if it is a lambda function.
        If the resource does not have a "FunctionName" property, it sets the "FunctionName" property to the resource name.

        Parameters:
            None

        Returns:
            None
        """
        for resource_name, resource_details in self.parsed_yaml["Resources"].items():
            if resource_details["Type"] == "AWS::Serverless::Function":
                if not "FunctionName" in resource_details["Properties"].keys():
                    resource_details["Properties"]["FunctionName"] = resource_name

    def add_resource_policies(self, graph: Graph):
        for resource in graph.resources:
            if resource.type == ResourceType.FUNCTION:
                self.parsed_yaml["Resources"][f"{resource.name}Policy"] = {
                    "Type": "AWS::Lambda::Permission",
                    "Properties": {
                        "Action": "lambda:InvokeFunction",
                        "FunctionName": {"Fn::GetAtt": [resource.name, "Arn"]},
                        "Principal": "events.amazonaws.com",
                    },
                }
            if resource.type == ResourceType.S3_BUCKET:
                self.parsed_yaml["Resources"][f"{resource.name}Policy"] = {
                    "Type": "AWS::S3::BucketPolicy",
                    "Properties": {
                        "Bucket": {"Ref": resource.name},
                        "PolicyDocument": {
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Principal": {
                                        "Service": "lambda.amazonaws.com",
                                    },
                                    "Action": list(resource.policy_actions),
                                    "Resource": {
                                        "Fn::Sub": f"arn:aws:s3:::${{{resource.name}}}/*"
                                    },
                                }
                            ]
                        },
                    },
                }

    def add_iam_roles(self, graph: Graph):
        for node in graph.nodes:
            if node.scope == Scope.GLOBAL:
                tree = node.object_fn.code_tree
                method = self.extract_method(tree=tree, node=node)
                iam_policy = self.generate_iam_policy(method, node)
                node.object_fn.iam_policies.append(iam_policy)
        for function in graph.functions:
            if function.iam_policies:
                self.parsed_yaml["Resources"][function.name]["Properties"].pop(
                    "Policies", None
                )
                self.parsed_yaml["Resources"][function.name]["Properties"].pop(
                    "Role", None
                )
                self.parsed_yaml["Resources"][function.name].pop("Connectors", None)
                self.parsed_yaml["Resources"][f"{function.name}Role"] = {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Principal": {"Service": "lambda.amazonaws.com"},
                                    "Action": "sts:AssumeRole",
                                }
                            ],
                        },
                        "Policies": [
                            {
                                "PolicyName": "root",
                                "PolicyDocument": {
                                    "Version": "2012-10-17",
                                    "Statement": function.iam_policies,
                                },
                            }
                        ],
                        "ManagedPolicyArns": [
                            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                        ],
                    },
                }
                self.parsed_yaml["Resources"][function.name]["Properties"]["Role"] = {
                    "Fn::GetAtt": [f"{function.name}Role", "Arn"]
                }

    def extract_method(self, tree, node: Node, method=None):
        """
        Extracts the method name from the given AST tree and node.

        Args:
            tree (AST): The AST tree to search for the method.
            node (Node): The node representing the method.
            method (str, optional): The extracted method name. Defaults to None.

        Returns:
            str: The extracted method name.
        """
        start_line = node.object_code_location["physicalLocation"]["region"][
            "startLine"
        ]
        end_line = node.object_code_location["physicalLocation"]["region"].get(
            "endLine", start_line
        )
        if getattr(tree, "body", None):
            for ast_node in tree.body:
                if (
                    getattr(ast_node, "lineno", None) == start_line
                    and getattr(ast_node, "end_lineno", None) == end_line
                ):
                    if node.object_type == "S3_BUCKET":
                        method = ast_node.value.func.attr
                    elif node.object_type == "DYNAMODB_TABLE":
                        if isinstance(ast_node.value, ast.Call):
                            method = ast_node.value.func.attr
                        elif isinstance(ast_node.value, ast.Subscript):
                            method = ast_node.value.value.func.attr
                        else:
                            raise NotImplementedError
                    elif node.object_type == "LAMBDA_INVOKE":
                        method = ast_node.value.func.attr
                    else:
                        raise NotImplementedError
                method = self.extract_method(ast_node, node, method=method)
        return method

    def generate_iam_policy(self, method, node: Node):
        """
        Generates an IAM policy based on the provided method and node.

        Args:
            method (str): The method for which the IAM policy is being generated.
            node (Node): The node object representing the resource.

        Returns:
            dict: The generated IAM policy.
        """
        actions = []
        if node.object_type == "S3_BUCKET":
            if method == "download_file":
                actions.append("s3:GetObject")
            elif method == "upload_file":
                actions.append("s3:PutObject")
        elif node.object_type == "DYNAMODB_TABLE":
            if method == "get_item":
                actions.append("dynamodb:GetItem")
            elif method == "put_item":
                actions.append("dynamodb:PutItem")
        elif node.object_type == "LAMBDA_INVOKE":
            if method == "invoke":
                actions.append("lambda:InvokeFunction")
            else:
                logger.error("Unsupported method: %s", method)
                raise NotImplementedError
        else:
            logger.error("Unsupported resource type: %s", node.object_type)
            raise NotImplementedError
        resources = node.resource_attrs["potential_resources"]
        for resource in resources:
            resource.policy_actions.update(actions)
        return {
            "Effect": "Allow",
            "Action": actions,
            "Resource": [
                {"Fn::GetAtt": [resource.name, "Arn"]} for resource in resources
            ],
        }

    def add_lambda_layer(self):
        """
        Adds the pydatalog lambda layer to the parsed YAML.

        This method copies the existing layer to the growlithe folder, then adds a new layer to the parsed YAML under the key "GrowlithePyDatalogLayer".
        Additionally, it adds the "GrowlithePyDatalogLayer" to the "Layers" property of all the lambda function resources.

        Returns:
        - None
        """
        self.copy_layer()
        self.parsed_yaml["Resources"]["GrowlithePyDatalogLayer"] = {
            "Type": "AWS::Serverless::LayerVersion",
            "Properties": {
                "LayerName": "GrowlithePyDatalogLayer",
                "CompatibleArchitectures": ["x86_64"],
                "ContentUri": "layers/pydatalog.zip",
                "Description": "PyDatalog layer for Growlithe",
                "CompatibleRuntimes": ["python3.10", "python3.9", "python3.8"],
            },
        }
        for _, resource_details in self.parsed_yaml["Resources"].items():
            if resource_details["Type"] == "AWS::Serverless::Function":
                if not "Layers" in resource_details["Properties"].keys():
                    resource_details["Properties"]["Layers"] = []
                resource_details["Properties"]["Layers"].append(
                    {"Ref": "GrowlithePyDatalogLayer"}
                )

    def copy_layer(self):
        """
        Copies the PyDatalog layer to the growlithe location.

        Returns:
            None
        """
        destination = os.path.join(
            self.config.growlithe_path, "layers", "pydatalog.zip"
        )
        os.makedirs(destination, exist_ok=True)
        shutil.copy(self.config.pydatalog_layer_path, destination)

    def save_config(self):
        """
        Save the updated configuration to a YAML file in the growlithe folder.

        Returns:
            None
        """
        if self.step_function_path:
            self.copy_step_function()
        self.copy_config_toml()
        path = self.config.growlithe_path
        config_path = os.path.join(path, "template.yml")
        with open(config_path, "w", encoding="utf-8") as f:
            dumper = yaml_dumper.get_dumper(clean_up=True, long_form=False)
            raw = yaml.dump(
                self.parsed_yaml,
                Dumper=dumper,
                default_flow_style=False,
                allow_unicode=True,
            )
            f.write(raw)
        logger.info("Saved updated configuration to %s", config_path)

    def copy_step_function(self):
        """
        Copies the step function definition to the growlithe location.

        Returns:
            None
        """
        destination = self.config.growlithe_path
        shutil.copy(self.step_function_path, destination)

    def copy_config_toml(self):
        """
        Copies the 'samconfig.toml' file from the app_path to the growlithe_path.

        Returns:
            None
        """
        path = os.path.join(self.config.app_path, "samconfig.toml")
        destination = os.path.join(self.config.growlithe_path, "samconfig.toml")
        if os.path.exists(path):
            shutil.copy(path, destination)
