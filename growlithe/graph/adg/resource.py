"""
Module for representing resources in an Application Dependency Graph (ADG).

This module defines the ResourceType enum and the Resource class, which are used
to represent different types of resources and their relationships in an application.
"""

from enum import Enum


class ResourceType(Enum):
    """
    Enum class to define the types of resources in the application.

    Each enum value represents a specific AWS resource type.
    """

    S3_BUCKET = "AWS::S3::Bucket"
    DYNAMODB = "AWS::DynamoDB::Table"
    FUNCTION = "AWS::Serverless::Function"
    STEP_FUNCTION = "AWS::Serverless::StateMachine"
    CONNECTOR = "AWS::Serverless::Connector"
    API = "AWS::Serverless::Api"
    AUTHORIZER = "AWS::ApiGateway::Authorizer"
    IDENTITY_POOL = "AWS::Cognito::IdentityPool"
    USER_POOL_CLIENT = "AWS::Cognito::UserPoolClient"
    USER_POOL = "AWS::Cognito::UserPool"
    IAM_ROLE = "AWS::IAM::Role"
    IAM_POLICY = "AWS::IAM::Policy"
    LAMBDA_PERMISSION = "AWS::Lambda::Permission"


class Resource:
    """
    Represents a resource in the Application Dependency Graph (ADG).

    This class encapsulates the properties and relationships of individual
    resources within the application structure.
    """

    def __init__(self, name, type, metadata=dict(), deployed_region=None):
        """
        Initialize a Resource instance.

        Args:
            name (str): Name of the resource.
            type (ResourceType): Type of the resource.
            metadata (dict, optional): Additional metadata for the resource. Defaults to an empty dict.
            deployed_region (str, optional): Region where the resource is deployed. Defaults to None.
        """
        self.name = name  # Name of the resource
        self.type: ResourceType = type  # Type of the resource
        self.metadata = metadata  # Additional metadata for the resource
        self.dependencies = []  # List of resources that this resource depends on
        self.trigger = None  # Resource that triggers this resource
        self.trigger_type = None  # Type of the triggering resource
        self.policy_actions = (
            set()
        )  # Set of policy actions associated with this resource
        self.deployed_region = deployed_region  # Region where the resource is deployed

    def __str__(self) -> str:
        """
        Return a string representation of the resource.

        Returns:
            str: String representation of the resource.
        """
        pass

    def __repr__(self) -> str:
        """
        Return a detailed string representation of the resource.

        Returns:
            str: Name of the resource.
        """
        return self.name

    def add_dependency(self, resource):
        """
        Add a dependency to this resource and set this resource as the trigger for the dependent resource.

        Args:
            resource (Resource): The resource that depends on this resource.
        """
        self.dependencies.append(resource)
        resource.trigger = self
        resource.trigger_type = self.type

    def visualize_dependencies(self):
        """
        Visualize the dependencies of this resource by printing them to the console.

        If the resource has no dependencies, it prints only the resource name.
        If it has dependencies, it prints the resource name followed by its dependencies.
        """
        if not self.dependencies:
            print(self.name)
        else:
            print(f"{self.name} -> {', '.join([r.name for r in self.dependencies])}")
