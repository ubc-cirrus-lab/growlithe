"""
Parses an AWS SAM template file to give a list of resource and their properties like events
"""

import os
import json
import yaml

from typing import List
from cfn_flip import load_yaml, yaml_dumper
from growlithe.common.file_utils import get_file_extension
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
        self.resources: List[Resource] = self.parse()

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

    def parse(self):
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
                resource: Resource = Resource(
                    name=resource_name,
                    type=ResourceType(resource_details["Type"]),
                    metadata=resource_details["Properties"],
                )
            if resource_details["Type"] == "AWS::Serverless::StateMachine":
                definition_uri: str = os.path.join(
                    *resource_details["Properties"]["DefinitionUri"].split(os.sep)
                )
                sam_file_dir: str = os.path.dirname(self.sam_file)
                definition_path: str = os.path.join(sam_file_dir, definition_uri)
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
        self.add_lambda_layer()
        self.add_iam_roles(graph)
        self.add_resource_policies(graph)

        self.save_config()

    def add_resource_policies(self, graph: Graph):
        for resource in graph.resources:
            if resource.type == ResourceType.FUNCTION:
                self.parsed_yaml["Resources"][f"{resource.name}Policy"] = {
                    "Type": "AWS::Lambda::Permission",
                    "Properties": {
                        "Action": "lambda:InvokeFunction",
                        "FunctionName": f"!Ref {resource.name}",
                        "Principal": "events.amazonaws.com",
                    },
                }
            if resource.type == ResourceType.S3_BUCKET:
                self.parsed_yaml["Resources"][f"{resource.name}Policy"] = {
                    "Type": "AWS::S3::BucketPolicy",
                    "Properties": {
                        "Bucket": f"!Ref {resource.name}",
                        "PolicyDocument": {
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Principal": {"Service": "lambda.amazonaws.com"},
                                    "Action": list(resource.policy_actions),
                                    "Resource": f"!Sub arn:aws:s3:::${resource.name}/*",
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
                self.parsed_yaml["Resources"][function.name]["Properties"][
                    "Policies"
                ] = {"Statement": function.iam_policies}

    def extract_method(self, tree, node: Node, method=None):
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
                    method = ast_node.value.func.attr
                method = self.extract_method(ast_node, node, method=method)
        return method

    def generate_iam_policy(self, method, node: Node):
        actions = []
        if node.object_type == "S3_BUCKET":
            if method == "download_file":
                actions.append("s3:GetObject")
            elif method == "upload_file":
                actions.append("s3:PutObject")
        resources = node.resource_attrs["potential_resources"]
        for resource in resources:
            resource.policy_actions.update(actions)
        return {
            "Effect": "Allow",
            "Action": actions,
            "Resource": [f"!Ref {resource.name}" for resource in resources],
        }

    def add_lambda_layer(self):
        layer_arn = self.config.growlithe_layer_arn
        for _, resource_details in self.parsed_yaml["Resources"].items():
            if resource_details["Type"] == "AWS::Serverless::Function":
                if "Layers" in resource_details["Properties"].keys():
                    resource_details["Properties"]["Layers"].append(layer_arn)
                else:
                    resource_details["Properties"]["Layers"] = [layer_arn]

    def save_config(self):
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
