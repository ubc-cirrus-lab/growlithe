from enum import Enum


class ResourceType(Enum):
    """
    Enum class to define the type of resource.
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


class Resource:
    def __init__(self, name, type, metadata=dict()):
        self.name = name
        self.type: ResourceType = type
        self.metadata = metadata
        self.dependencies = []
        self.trigger = None
        self.trigger_type = None

    def __str__(self) -> str:
        pass

    def __repr__(self) -> str:
        return self.name

    def add_dependency(self, resource):
        self.dependencies.append(resource)
        resource.trigger = self
        resource.trigger_type = self.type
    
    def visualize_dependencies(self):
        if not self.dependencies:
            print(self.name)
        else:
            print(f"{self.name} -> {', '.join([r.name for r in self.dependencies])}")
