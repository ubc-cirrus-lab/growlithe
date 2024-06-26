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
        for resource in resources:
            # Add workflow dependency edges
            for dependency in resource.dependencies:
                if isinstance(resource, Function):
                    source = resource.get_return_node()
                else:
                    event = [event for event in dependency.metadata["Events"].values()][0]
                    if resource.type == 'AWS::DynamoDB::Table':
                        source = Node(
                                Reference(
                                    ReferenceType.STATIC,
                                    event["Properties"]["Stream"]["Fn::GetAtt"][0],
                                ),
                                Reference(
                                ReferenceType.DYNAMIC, ""
                                ), #PRAVEEN: Don't know what goes here
                                "DynamoDB",
                                None,
                                None,
                                dependency,
                                {},
                                {},
                                Scope.GLOBAL,
                            )
                    elif resource.type == 'AWS::Serverless::Api':
                        source = Node(
                                Reference(
                                    ReferenceType.STATIC,
                                    event["Properties"]["RestApiId"]["Ref"],
                                ),
                                Reference(
                                ReferenceType.DYNAMIC, event["Properties"]["Path"]
                                ),
                                "API-GET",
                                None,
                                None,
                                dependency,
                                {},
                                {},
                                Scope.GLOBAL,
                            )
                    #TODO: add bucket trigger
                    self.graph.add_node(source)
                if isinstance(dependency, Function):
                    sink = dependency.get_event_node()                        
                    self.graph.add_edge(
                        Edge(
                            source,
                            sink,
                            source.object_code_location,
                            sink.object_code_location,
                            dependency,
                            EdgeType.INDIRECT #PRAVEEN: check
                        )
                    )

        # Add lambda invoke dependency edges
        for node in self.graph.nodes:
            if node.object_type == 'LAMBDA_INVOKE':
                for function in self.graph.functions:
                    if function.name in node.resource.reference_name:
                        self.graph.add_edge(
                            Edge(
                                node,
                                function.get_event_node(),
                                node.object_code_location,
                                function.get_event_node().object_code_location,
                                None,
                                EdgeType.INDIRECT
                            )
                        )

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

    def add_indirect_edges(self, functions: List[Function]):
        """
        
For each of the above pairs (f1,f2), we now add edges (of type INDIRECT) for read-after-write operations performed on objects in persisted data stores shared across f1, f2.

We define Nw in Vf1 as nodes representing persisted data objects with an incoming edge (i.e. has a write operation on them).
Similarly, we define Nr in Vf2 as nodes representing persisted data objects with an outgoing edge (i.e. has a read operation on them).

For nw in Nw:
	For nr in Nr:
		// Both nodes have same object type
		If node_props[nw].ObjType == node_props[nr].ObjType &&
		//The nodes have a possible offline taint label match
match_labels(offline_taint_label(nw), offline_taint_label(nw)) in [‘Match’, ‘PossibleMatch’]:
//exists a path from upstreamMetaNodes(nw) to upstreamMetaNodes(nr):
For mw in upstreamMetaNodes(nw):
	For mr in upstreamMetaNodes(nr):
	If mw in TransitiveUpstreamNodes[mr]
			Add an edge from nw to nr with edgeType INDIRECT

        """
        for function1 in functions:
            # TODO: Change dependencies to next func (dependenceis seems opposite)
            for function2 in function1.dependencies:
                for node1 in function1.nodes:
                    for node2 in function2.nodes:
                        if node1.object_type == node2.object_type:
                            if node1.incoming_edges and node2.outgoing_edges:
                                if node1.offline_match(node2) in [TaintLabelMatch.MATCH, TaintLabelMatch.POSSIBLE_MATCH]:
                                    pass
                                        
