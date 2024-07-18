import os
from typing import List
from graph.adg.edge import Edge, EdgeType
from graph.adg.graph import Graph
from graph.adg.node import Node
from graph.adg.function import Function
from graph.adg.resource import Resource
from graph.adg.types import Reference, ReferenceType, Scope, TaintLabelMatch
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
        for source in resources:
            for target in source.dependencies:
                # source -> target
                if isinstance(target, Function):
                    if isinstance(source, Function):
                        # Function chain
                        self.connect_functions(source, target)
                    else:
                        # trigger
                        self.add_trigger_edge(source, target)
                else:
                    # should not happen
                    logger.error(f"{source.name}:{source.type} -> {target.name}:{target.type} is not supported.")

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

    def add_trigger_edge(self, source: Resource, target: Function):
        pass
