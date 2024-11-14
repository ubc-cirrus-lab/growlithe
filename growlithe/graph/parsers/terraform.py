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
        self.terraform_resources = {}

    @profiler_decorator
    def parse_template(self):
        resources: List[Resource] = []
        with open(self.sam_file, "r") as f:
            self.parsed_yaml = hcl2.load(f)
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
        self.add_iam_roles(graph)
        # self.add_resource_policies(graph)

    def add_resource_policies(self, graph: Graph):
        for resource in graph.resources:
            if resource.type == ResourceType.FUNCTION:
                # For GCP Cloud Functions, add IAM policy to allow invocation
                policy_resource = {
                    "google_cloudfunctions_function_iam_member": {
                        f"{resource.name}_invoker": {
                            "project": resource.metadata.get(
                                "project", "${var.project_id}"
                            ),
                            "region": resource.metadata.get("region", "${var.region}"),
                            "cloud_function": resource.name,
                            "role": "roles/cloudfunctions.invoker",
                            "member": "allUsers",  # Adjust as necessary
                        }
                    }
                }
                self.parsed_yaml.setdefault("resource", []).append(policy_resource)
            elif resource.type == ResourceType.S3_BUCKET:
                # For GCS Buckets, add IAM policies
                for action in resource.policy_actions:
                    role = self.map_storage_action_to_role(action)
                    policy_resource = {
                        "google_storage_bucket_iam_member": {
                            f"{resource.name}_{role.replace('/', '_')}_binding": {
                                "bucket": resource.name,
                                "role": role,
                                "member": "serviceAccount:${{var.service_account_email}}",  # Adjust as needed
                            }
                        }
                    }
                    self.parsed_yaml.setdefault("resource", []).append(policy_resource)

    def add_iam_roles(self, graph: Graph):
        for node in graph.nodes:
            if node.scope == Scope.GLOBAL:
                tree = node.object_fn.code_tree
                method = self.extract_method(tree=tree, node=node)
                iam_policy = self.generate_iam_policy(method, node)
                node.object_fn.iam_policies.append(iam_policy)
        for function in graph.functions:
            if function.iam_policies:
                # Create a service account for the Cloud Function
                sa_resource_name = f"{function.name}_service_account"
                sa_resource = {
                    "google_service_account": {
                        sa_resource_name: {
                            "account_id": f"{function.name}-sa",
                            "display_name": f"{function.name} Service Account",
                        }
                    }
                }
                self.parsed_yaml.setdefault("resource", []).append(sa_resource)
                # Assign roles to the service account
                for iam_policy in function.iam_policies:
                    for role in iam_policy["Roles"]:
                        binding_name = (
                            f"{function.name}_{role.replace('/', '_')}_binding"
                        )
                        iam_member_resource = {
                            "google_project_iam_member": {
                                binding_name: {
                                    "project": "${var.project_id}",
                                    "role": role,
                                    "member": f"serviceAccount:${{google_service_account.{sa_resource_name}.email}}",
                                }
                            }
                        }
                        self.parsed_yaml.setdefault("resource", []).append(
                            iam_member_resource
                        )
                # Attach the service account to the Cloud Function
                # Find the Cloud Function resource and update it
                for resource in self.parsed_yaml.get("resource", []):
                    if "google_cloudfunctions_function" in resource:
                        func_config = resource["google_cloudfunctions_function"]
                        if function.name in func_config:
                            func_config[function.name][
                                "service_account_email"
                            ] = f"${{google_service_account.{sa_resource_name}.email}}"
                            break

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
                    if node.object_type == "GCS_BUCKET":
                        method = ast_node.value.func.attr
                    elif node.object_type == "CLOUD_FUNCTION":
                        method = ast_node.value.func.attr
                    elif node.object_type == "FIRESTORE_COLLECTION":
                        method = ast_node.value.func.attr
                    else:
                        raise NotImplementedError(
                            f"{node.object_type} is Unsupported GCP resource type"
                        )
                method = self.extract_method(ast_node, node, method=method)
        return method

    def generate_iam_policy(self, method, node: Node):
        roles = []
        if node.object_type == "GCS_BUCKET":
            if method == "download_blob":
                roles.append("roles/storage.objectViewer")
            elif method == "upload_blob":
                roles.append("roles/storage.objectCreator")
        elif node.object_type == "CLOUD_FUNCTION":
            if method == "call_function":
                roles.append("roles/cloudfunctions.invoker")
            else:
                logger.error("Unsupported method: %s", method)
                raise NotImplementedError("Unsupported method for Cloud Function")
        elif node.object_type == "FIRESTORE_COLLECTION":
            if method == "query":
                roles.append("roles/datastore.viewer")
            elif method == "insert":
                roles.append("roles/datastore.user")
            elif method == "delete":
                roles.append("roles/datastore.owner")
        else:
            logger.error("Unsupported resource type: %s", node.object_type)
            raise NotImplementedError(
                f"Unsupported GCP resource type: {node.object_type}"
            )
        return {"Effect": "Allow", "Roles": roles}

    def map_storage_action_to_role(self, action):
        action_role_mapping = {
            "storage.objects.get": "roles/storage.objectViewer",
            "storage.objects.create": "roles/storage.objectCreator",
            "storage.objects.delete": "roles/storage.objectAdmin",
        }
        return action_role_mapping.get(action, "roles/storage.objectAdmin")

    def copy_layer(self):
        destination = os.path.join(
            self.config.growlithe_path, "layers", "pydatalog.zip"
        )
        os.makedirs(destination, exist_ok=True)
        if os.exists(self.config.pydatalog_layer_path):
            shutil.copy(self.config.pydatalog_layer_path, destination)
        else:
            logger.warning(f"No zip found at {self.config.pydatalog_layer_path}")

    def save_config(self):
        """
        Save the updated configuration to a YAML file in the growlithe folder.

        Returns:
            None
        """
        path = self.config.growlithe_path
        config_path = os.path.join(path, "main.tf.json")
        with open(config_path, "w") as file:
            json.dump(self.parsed_yaml, file, indent=4)

        logger.info("Saved updated configuration to %s", config_path)
