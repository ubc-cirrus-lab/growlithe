"""
Parses an AWS SAM template file to give a list of resource and their properties like events
"""

from typing import List
from cfn_flip import load_yaml
from graph.adg.resource import Resource
from graph.adg.function import Function


class SAMParser:
    def __init__(self, sam_file):
        self.sam_file: str = sam_file
        self.resources: List[Resource] = self.parse()
        # for resource in self.resources:
        #     resource.visualize_dependencies()

    def parse(self):
        resources: List[Resource] = []
        with open(self.sam_file, "r") as f:
            config: dict = load_yaml(f.read())
        for resource_name, resource_details in config["Resources"].items():
            if resource_details["Type"] == "AWS::Serverless::Function":
                resource: Resource = Function(
                    name=resource_name,
                    type=resource_details["Type"],
                    runtime=resource_details["Properties"]["Runtime"],
                    path=resource_details["Properties"]["CodeUri"],
                    metadata=resource_details["Properties"],
                )
            else:
                resource: Resource = Resource(
                    name=resource_name,
                    type=resource_details["Type"],
                    metadata=resource_details["Properties"],
                )
            if resource_details["Type"] == "AWS::Serverless::StateMachine":
                definition_uri = resource_details["Properties"]["DefinitionUri"]
                print(definition_uri)
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
                        ref.extend(bucket["Ref"] for bucket in properties["Pattern"]["detail"]["bucket"]["name"])
                    source_resource: Resource = None
                    for ref in ref:
                        for res in resources:
                            if ref == res.name:
                                source_resource = res
                        source_resource.add_dependency(resource)

        return resources

    def get_functions(self) -> List[Function]:
        return [
            resource for resource in self.resources if isinstance(resource, Function)
        ]

    def get_resources(self) -> List[Resource]:
        return self.resources

    def get_events(self):
        pass
