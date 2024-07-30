from sarif import loader
import os
import re

from growlithe.graph.adg.edge import Edge, EdgeType
from growlithe.graph.adg.function import Function
from growlithe.graph.adg.graph import Graph
from growlithe.graph.adg.node import Node
from growlithe.graph.adg.types import InterfaceType, Reference, ReferenceType, Scope
from growlithe.common.logger import logger


class SarifParser:
    def __init__(self, sarif_output_path):
        self.sarif_output_path = sarif_output_path
        self.results = loader.load_sarif_file(sarif_output_path).get_results()

    def get_results_for_function(self, function: Function):
        return [
            result
            for result in self.results
            if result["locations"][0]["physicalLocation"]["artifactLocation"][
                "uri"
            ].startswith(function.path)
        ]

    def parse_sarif_result(self, result, graph: Graph, function: Function, edge_type):
        related_locations = result["relatedLocations"]
        for flow in result["message"]["text"].split("\n"):
            """
            Flows are typically in form of
            "[SOURCE, GLOBAL, S3_BUCKET:STATIC:imageprocessingbenchmark, STATIC:sample_2.png](1)
            ==>[SINK, CONTAINER, LOCAL_FILE:STATIC:tempfs, DYNAMIC:tempFile](2)"
            """
            self.parse_sarif_flow(flow, graph, related_locations, function, edge_type)

    def parse_sarif_flow(
        self,
        flow,
        graph: Graph,
        related_locations,
        function: Function,
        edge_type: EdgeType,
    ):

        flow_ends = flow.split("==>")

        if len(flow_ends) == 2:
            source_side, sink_side = flow_ends

            # Parse source side
            source_node, source_location = self.create_node_from_side(
                source_side, related_locations, function
            )

            # Parse sink side
            sink_node, sink_location = self.create_node_from_side(
                sink_side, related_locations, function
            )
            if source_node:
                source_node = graph.add_node(source_node)
            if sink_node:
                sink_node = graph.add_node(sink_node)

            if source_node and sink_node and source_node != sink_node:
                edge = Edge(
                    source_node,
                    sink_node,
                    {"CodePath": source_location},
                    {"CodePath": sink_location},
                    function,
                    edge_type,
                )
                graph.add_edge(edge)
        else:
            logger.error(f"Invalid flow format: {flow}")

    def create_node_from_side(self, node_str, related_locations, function: Function):
        if "None" in node_str:
            # logger.warning("Side is None. Creating a default node")
            return None, None

        match = re.match(
            r"\[([^,]+),\s([^,]+),\s([^:]+):([^:]+):([^,]+),\s([^:]+):([^:]+)\]\((\d+)\)",
            node_str,
        )
        if match:
            groups = match.groups()
            interface_type = InterfaceType[groups[0]]
            scope = Scope[groups[1]]
            object_type = groups[2]
            resource_reference_type = ReferenceType[groups[3]]
            resource_reference_name = groups[4]
            object_reference_type = ReferenceType[groups[5]]
            object_reference_name = groups[6]

            code_path = related_locations[int(groups[7]) - 1]
            node = Node(
                Reference(resource_reference_type, resource_reference_name),
                Reference(object_reference_type, object_reference_name),
                object_type,
                None,  # TODO: Extend static analysis to add handler
                code_path,
                function,
                {},
                {},
                scope,
            )
            return node, code_path
        else:
            logger.error(f"Invalid format when parsing node str: {node_str}")
            return None, None
