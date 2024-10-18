"""
Parses a terraform template file to give a list of resource and their properties like events (currently only for gcp and assumming all terraform resources are defined in a single file)
"""

import os
import hcl2
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


class TerraformParser:
    def __init__(self, sam_file, config):
        self.sam_file: str = sam_file
        self.config: Config = config
        self.parsed_yaml = None
        self.step_function_path = None
        self.resources: List[Resource] = self.parse_template()
        self.deployed_region = None

    @profiler_decorator
    def parse_template(self):
        resources: List[Resource] = []
        with open(self.sam_file, "r") as f:
            self.parsed_yaml = hcl2.load(f)
            with open("main.tf.json", "w") as file:
                json.dump(self.parsed_yaml, file, indent=4)
        for terraform_block in self.parsed_yaml.get("provider", []):
            self.deployed_region = terraform_block.get("google", {}).get("region")
        backend_buckets = set()
        for terraform_block in self.parsed_yaml.get("terraform", []):
            for backend in terraform_block.get("backend", []):
                if "gcs" in backend:
                    backend_buckets.add(backend["gcs"]["bucket"])

        for resource in self.parsed_yaml.get("resource", []):
            resource_type = list(resource.keys())[0]
            resource_body = resource[resource_type]
            resource_name = list(resource_body.keys())[0]
            resource_config = resource_body[resource_name]

            if resource_type == "google_cloudfunctions_function":
                code_uri = resource_config["entry_point"]
                # handler = resource_config["entry_point"]
                handler = "app"
                runtime = resource_config["runtime"]
                handler_path = handler
                file_extension = get_file_extension(runtime)

                # Construct the full path to the Lambda function's code
                function_path = os.path.normpath(
                    os.path.join(
                        self.config.src_path,
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
                    type=ResourceType.FUNCTION,
                    runtime=runtime,
                    function_path=function_path,
                    growlithe_function_path=growlithe_function_path,
                    metadata=resource_config,
                    deployed_region=self.deployed_region,
                )
            else:
                try:
                    resource_mapping = {
                        "google_storage_bucket": ResourceType.S3_BUCKET,
                        "google_storage_bucket_object": ResourceType.S3_BUCKET,
                        "google_cloudfunctions_function_iam_member": ResourceType.IAM_ROLE,
                        "google_firestore_database": ResourceType.DYNAMODB,
                    }
                    resource: Resource = Resource(
                        name=resource_name,
                        type=resource_mapping[resource_type],
                        metadata=resource_config,
                        deployed_region=self.deployed_region,
                    )
                except ValueError:
                    logger.warning("Unsupported resource type: %s", resource_type)
            resources.append(resource)
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
        # TODO: Add alternative way of adding pyDatalog dependency for GCP
        # TODO: Same for IAM
        # self.add_lambda_layer()
        # self.add_iam_roles(graph)
        # self.add_resource_policies(graph)
        logger.error("Not implemented, generate GCP updated terraform config")

    # def add_resource_policies(self, graph: Graph):
    #     for resource in graph.resources:
    #         if resource.type == ResourceType.FUNCTION:
    #             self.parsed_yaml["Resources"][f"{resource.name}Policy"] = {
    #                 "Type": "AWS::Lambda::Permission",
    #                 "Properties": {
    #                     "Action": "lambda:InvokeFunction",
    #                     "FunctionName": {"Fn::GetAtt": [resource.name, "Arn"]},
    #                     "Principal": "events.amazonaws.com",
    #                 },
    #             }
    #         if resource.type == ResourceType.S3_BUCKET:
    #             self.parsed_yaml["Resources"][f"{resource.name}Policy"] = {
    #                 "Type": "AWS::S3::BucketPolicy",
    #                 "Properties": {
    #                     "Bucket": {"Ref": resource.name},
    #                     "PolicyDocument": {
    #                         "Statement": [
    #                             {
    #                                 "Effect": "Allow",
    #                                 "Principal": {
    #                                     "Service": "lambda.amazonaws.com",
    #                                 },
    #                                 "Action": list(resource.policy_actions),
    #                                 "Resource": {
    #                                     "Fn::Sub": f"arn:aws:s3:::${{{resource.name}}}/*"
    #                                 },
    #                             }
    #                         ]
    #                     },
    #                 },
    #             }

    # def add_iam_roles(self, graph: Graph):
    # for node in graph.nodes:
    #     if node.scope == Scope.GLOBAL:
    #         tree = node.object_fn.code_tree
    #         method = self.extract_method(tree=tree, node=node)
    #         iam_policy = self.generate_iam_policy(method, node)
    #         node.object_fn.iam_policies.append(iam_policy)
    # for function in graph.functions:
    #     if function.iam_policies:
    #         self.parsed_yaml["Resources"][function.name]["Properties"].pop(
    #             "Policies", None
    #         )
    #         self.parsed_yaml["Resources"][function.name]["Properties"].pop(
    #             "Role", None
    #         )
    #         self.parsed_yaml["Resources"][function.name].pop("Connectors", None)
    #         self.parsed_yaml["Resources"][f"{function.name}Role"] = {
    #             "Type": "AWS::IAM::Role",
    #             "Properties": {
    #                 "AssumeRolePolicyDocument": {
    #                     "Version": "2012-10-17",
    #                     "Statement": [
    #                         {
    #                             "Effect": "Allow",
    #                             "Principal": {"Service": "lambda.amazonaws.com"},
    #                             "Action": "sts:AssumeRole",
    #                         }
    #                     ],
    #                 },
    #                 "Policies": [
    #                     {
    #                         "PolicyName": "root",
    #                         "PolicyDocument": {
    #                             "Version": "2012-10-17",
    #                             "Statement": function.iam_policies,
    #                         },
    #                     }
    #                 ],
    #                 "ManagedPolicyArns": [
    #                     "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    #                 ],
    #             },
    #         }
    #         self.parsed_yaml["Resources"][function.name]["Properties"]["Role"] = {
    #             "Fn::GetAtt": [f"{function.name}Role", "Arn"]
    #         }

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
                        # TODO: Add support for GCP resources
                        raise NotImplementedError
                method = self.extract_method(ast_node, node, method=method)
        return method

    # def generate_iam_policy(self, method, node: Node):
    # """
    # Generates an IAM policy based on the provided method and node.

    # Args:
    #     method (str): The method for which the IAM policy is being generated.
    #     node (Node): The node object representing the resource.

    # Returns:
    #     dict: The generated IAM policy.
    # """
    # actions = []
    # if node.object_type == "S3_BUCKET":
    #     if method == "download_file":
    #         actions.append("s3:GetObject")
    #     elif method == "upload_file":
    #         actions.append("s3:PutObject")
    # elif node.object_type == "DYNAMODB_TABLE":
    #     if method == "get_item":
    #         actions.append("dynamodb:GetItem")
    #     elif method == "put_item":
    #         actions.append("dynamodb:PutItem")
    # elif node.object_type == "LAMBDA_INVOKE":
    #     if method == "invoke":
    #         actions.append("lambda:InvokeFunction")
    #     else:
    #         logger.error("Unsupported method: %s", method)
    #         raise NotImplementedError
    # else:
    #     logger.error("Unsupported resource type: %s", node.object_type)
    #     raise NotImplementedError
    # resources = node.resource_attrs["potential_resources"]
    # for resource in resources:
    #     resource.policy_actions.update(actions)
    # return {
    #     "Effect": "Allow",
    #     "Action": actions,
    #     "Resource": [
    #         {"Fn::GetAtt": [resource.name, "Arn"]} for resource in resources
    #     ],
    # }

    # def add_lambda_layer(self):
    #     """
    #     Adds the pydatalog lambda layer to the parsed YAML.

    #     This method copies the existing layer to the growlithe folder, then adds a new layer to the parsed YAML under the key "GrowlithePyDatalogLayer".
    #     Additionally, it adds the "GrowlithePyDatalogLayer" to the "Layers" property of all the lambda function resources.

    #     Returns:
    #     - None
    #     """
    #     self.copy_layer()
    #     self.parsed_yaml["Resources"]["GrowlithePyDatalogLayer"] = {
    #         "Type": "AWS::Serverless::LayerVersion",
    #         "Properties": {
    #             "LayerName": "GrowlithePyDatalogLayer",
    #             "CompatibleArchitectures": ["x86_64"],
    #             "ContentUri": "layers/pydatalog.zip",
    #             "Description": "PyDatalog layer for Growlithe",
    #             "CompatibleRuntimes": ["python3.10", "python3.9", "python3.8"],
    #         },
    #     }
    #     for _, resource_details in self.parsed_yaml["Resources"].items():
    #         if resource_details["Type"] == "AWS::Serverless::Function":
    #             if not "Layers" in resource_details["Properties"].keys():
    #                 resource_details["Properties"]["Layers"] = []
    #             resource_details["Properties"]["Layers"].append(
    #                 {"Ref": "GrowlithePyDatalogLayer"}
    #             )

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
        # """
        # Save the updated configuration to a YAML file in the growlithe folder.

        # Returns:
        #     None
        # """
        # if self.step_function_path:
        #     self.copy_step_function()
        # self.copy_config_toml()
        # path = self.config.growlithe_path
        # config_path = os.path.join(path, "template.yml")
        # with open(config_path, "w", encoding="utf-8") as f:
        #     dumper = yaml_dumper.get_dumper(clean_up=True, long_form=False)
        #     raw = yaml.dump(
        #         self.parsed_yaml,
        #         Dumper=dumper,
        #         default_flow_style=False,
        #         allow_unicode=True,
        #     )
        #     f.write(raw)
        # logger.info("Saved updated configuration to %s", config_path)
        logger.error("Implement Terraform config generator")

    # def copy_step_function(self):
    #     """
    #     Copies the step function definition to the growlithe location.

    #     Returns:
    #         None
    #     """
    #     destination = self.config.growlithe_path
    #     shutil.copy(self.step_function_path, destination)

    # def copy_config_toml(self):
    #     """
    #     Copies the 'samconfig.toml' file from the app_path to the growlithe_path.

    #     Returns:
    #         None
    #     """
    #     path = os.path.join(self.config.app_path, "samconfig.toml")
    #     destination = os.path.join(self.config.growlithe_path, "samconfig.toml")
    #     if os.path.exists(path):
    #         shutil.copy(path, destination)
