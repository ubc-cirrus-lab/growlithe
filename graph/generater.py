import os
from typing import List
from graph.adg.edge import Edge, EdgeType
from graph.adg.graph import Graph
from graph.adg.node import Node
from graph.adg.function import Function
from graph.adg.resource import Resource, ResourceType
from graph.adg.types import Scope
from graph.parsers.sarif import SarifParser
from common.app_config import growlithe_path, benchmark_name
from common.logger import logger


class GraphGenerator:
    def __init__(self, graph: Graph):
        self.graph: Graph = graph

    def generate_intrafunction_graphs(self, functions: List[Function]):
        language = "python"
        sarif_parser = SarifParser(
            os.path.join(growlithe_path, f"dataflows_{language}.sarif")
        )
        for function in functions:
            function_dataflows = sarif_parser.get_results_for_function(function)
            function.add_sarif_results(function_dataflows)
            for result in function_dataflows:
                sarif_parser.parse_sarif_result(result, self.graph, function, EdgeType.DATA)

    def add_inter_function_edges(self, resources: List[Resource]):
        function_pairs = []
        for source in resources:
            for target in source.dependencies:
                # source -> target
                if isinstance(target, Function):
                    if isinstance(source, Function):
                        # Function chain
                        self.connect_functions(source, target)
                        function_pairs.append((source, target))
                    else:
                        # trigger
                        self.handle_trigger(source, target)
                else:
                    # should not happen
                    logger.error(f"{source.name}:{source.type} -> {target.name}:{target.type} is not supported.")
        for (source, target) in function_pairs:
            self.add_potential_indirect_flows(source, target)


    def add_metadata_edges(self, functions: List[Function]):
        language = "python"
        sarif_parser = SarifParser(
            os.path.join(growlithe_path, f"metadataflows_{language}.sarif")
        )
        edge_type = EdgeType.METADATA
        if benchmark_name.startswith('Benchmark1') or benchmark_name.startswith('Benchmark3'):
            edge_type = EdgeType.DATA

        for function in functions:
            function_metadataflows = sarif_parser.get_results_for_function(function)
            # function.add_sarif_results(function_metadataflows)
            for result in function_metadataflows:
                sarif_parser.parse_sarif_result(result, self.graph, function, edge_type)

    def connect_functions(self, source: Function, target: Function):
        source_ret: Node = source.get_return_node()
        target_event: Node = target.get_event_node()
        edge = Edge(
            u=source_ret,
            v=target_event,
            source_code_path=source_ret.object_code_location,
            sink_code_path=target_event.object_code_location,
            function=source,
            edge_type=EdgeType.INDIRECT
        )
        self.graph.add_edge(edge)

    def handle_trigger(self, source: Resource, target: Function):
        # S3 trigger
        if source.type == ResourceType.S3_BUCKET:
            self.append_resource_metadata(source)
        # TODO: DynamoDB trigger

    def append_resource_metadata(self, resource: Resource):
        """
        Add potential resource to the node inside the function that represents the resource
        :param resource: Resource
        """
        for node in self.graph.nodes:
            if node.object_type == resource.type.name:
                if 'potential_resources' in node.resource_attrs:
                    node.resource_attrs['potential_resources'].append(resource)
                else:
                    node.resource_attrs['potential_resources'] = [resource]

    def add_potential_indirect_flows(self, source: Function, target: Function):
        """
        Add indirect edges from all the nodes in the source function to all the nodes in the sink function that share potential resources.
        :param source: source function
        :param target: target function
        """
        for node1 in self.graph.nodes:
            if node1.object_fn == source and node1.scope == Scope.GLOBAL and node1.is_sink:
                for node2 in self.graph.nodes:
                    if node2.object_fn == target and node2.scope == Scope.GLOBAL and node2.is_source:
                        if 'potential_resources' in node1.resource_attrs and 'potential_resources' in node2.resource_attrs:
                            for resource in node1.resource_attrs['potential_resources']:
                                if resource in node2.resource_attrs['potential_resources']:
                                    edge = Edge(
                                        u=node1,
                                        v=node2,
                                        source_code_path=node1.object_code_location,
                                        sink_code_path=node2.object_code_location,
                                        function=source,
                                        edge_type=EdgeType.INDIRECT
                                    )
                                    self.graph.add_edge(edge)
