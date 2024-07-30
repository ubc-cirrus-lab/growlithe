"""
Parses an AWS SAM template file to give a list of resource and their properties like events
"""
import os
import json

from typing import List
from cfn_flip import load_yaml
from growlithe.graph.adg.resource import Resource, ResourceType
from growlithe.graph.adg.function import Function
from growlithe.common.logger import logger
from growlithe.common.app_config import app_path

class SAMParser:
    def __init__(self, sam_file):
        self.sam_file: str = sam_file
        self.resources: List[Resource] = self.parse()


    def parse_state_machine(self, definition_path: str, step_function: Resource, resources: List[Resource]):
        substitutions = {}
        if 'DefinitionSubstitutions' in step_function.metadata.keys():
            for key, value in step_function.metadata['DefinitionSubstitutions'].items():
                substitutions[key] = value.items()[0][1][0] if value.items()[0][0] == 'Fn::GetAtt' else value

        with open(definition_path, "r") as f:
            states = json.loads(f.read())
        self.fix_dependencies(step_function=step_function, resources=resources, substitutions=substitutions, states=states)
        for _, state in states["States"].items():
            # get source function
            self.extract_dependencies(resources=resources, substitutions=substitutions, states=states, state=state)

    def extract_dependencies(self, resources, substitutions, states, state):
        source_function = None
        if state['Type'] == 'Task':
            source_function_name = state['Parameters']['FunctionName']
            if '$' in source_function_name:
                source_function_name = substitutions[source_function_name[2:-1]]
            source_function = self.find_resource(source_function_name, resources)

        if source_function and "Next" in state.keys():
            next_state = states["States"][state["Next"]]
            if next_state['Type'] == 'Task':
                target_function_name = next_state['Parameters']['FunctionName']
                if '$' in target_function_name:
                    target_function_name = substitutions[target_function_name[2:-1]]
                target_function = self.find_resource(target_function_name, resources)
                source_function.add_dependency(target_function)
            elif next_state['Type'] == 'Choice':
                for choice in next_state['Choices']:
                    target = choice['Next']
                    default = next_state['Default']
                    target_function_name = states["States"][target]['Parameters']['FunctionName']
                    default_function_name = states["States"][default]['Parameters']['FunctionName']
                    if '$' in target_function_name:
                        target_function_name = substitutions[target_function_name[2:-1]]
                    if '$' in default_function_name:
                        default_function_name = substitutions[default_function_name[2:-1]]
                    target_function = self.find_resource(target_function_name, resources)
                    default_function = self.find_resource(default_function_name, resources)
                    source_function.add_dependency(target_function)
                    source_function.add_dependency(default_function)
            elif next_state['Type'] == 'Catch':
                target = next_state['Next']
                target_function_name = states["States"][target]['Parameters']['FunctionName']
                if '$' in target_function_name:
                    target_function_name = substitutions[target_function_name[2:-1]]
                target_function = self.find_resource(target_function_name, resources)
                source_function.add_dependency(target_function)
            else:
                logger.error(f"Unsupported state type: {next_state['Type']}")
                raise NotImplementedError

    def fix_dependencies(self, step_function, resources, substitutions, states):
        start_state = states["States"][states["StartAt"]]
        function_name = start_state['Parameters']['FunctionName']
        if '$' in function_name:
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
            config: dict = load_yaml(f.read())
        for resource_name, resource_details in config["Resources"].items():
            if resource_details["Type"] == "AWS::Serverless::Function":
                resource: Resource = Function(
                    name=resource_name,
                    type=ResourceType(resource_details["Type"]),
                    runtime=resource_details["Properties"]["Runtime"],
                    path=resource_details["Properties"]["CodeUri"],
                    metadata=resource_details["Properties"],
                )
            else:
                resource: Resource = Resource(
                    name=resource_name,
                    type=ResourceType(resource_details["Type"]),
                    metadata=resource_details["Properties"],
                )
            if resource_details["Type"] == "AWS::Serverless::StateMachine":
                definition_uri: str = os.path.join(*resource_details["Properties"]["DefinitionUri"].split(os.sep))
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
                        ref.extend(bucket["Ref"] for bucket in properties["Pattern"]["detail"]["bucket"]["name"])
                    source_resource: Resource = None
                    for ref in ref:
                        source_resource = self.find_resource(ref=ref, resources=resources)
                        source_resource.add_dependency(resource)
        if has_step_function:
            self.parse_state_machine(definition_path=definition_path, step_function=parent_step_function, resources=resources)
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

    def get_events(self):
        pass
