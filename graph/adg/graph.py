import json
from typing import List
from common.logger import logger
from graph.adg.node import Node
from graph.adg.edge import Edge, EdgeType
from graph.adg.function import Function
from graph.adg.resource import Resource
from graph.adg.types import Scope


class Graph:
    def __init__(self, name: str = ""):
        self.name: str = name
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.metadata_edges: List[Edge] = []

        self.functions: List[Function] = []
        self.resources: List[Resource] = []

    def add_node(self, new_node: Node):
        # Check if a node with the same properties already exists in the graph
        for existing_node in self.nodes:
            if existing_node == new_node:
                # logger.info('Using existing node for metadata')
                return existing_node
        self.nodes.append(new_node)
        if new_node.object_fn:
            new_node.object_fn.add_node(new_node)
            
        if new_node.object_type == "PARAM":
            new_node.object_fn.add_event_node(new_node)

        if new_node.object_type == "RETURN":
            new_node.object_fn.add_return_node(new_node)
        return new_node

    def add_edge(self, edge: Edge):
        for existing_edge in self.edges:
            if existing_edge == edge:
                return existing_edge
        if edge.edge_type == EdgeType.METADATA:
            self.metadata_edges.append(edge)
        else:
            self.edges.append(edge)
        edge.source.outgoing_edges.append(edge)
        edge.sink.incoming_edges.append(edge)
        return edge

    def add_functions(self, functions: Function):
        self.functions = functions

    def add_resources(self, resources: Resource):
        self.resources = resources
    
    def visualize(self):
        adj_list = {str(node): [] for node in self.nodes}
        for edge in self.edges:
            adj_list[str(edge.source)].append(edge.sink)

        for node in self.nodes:
            if len(adj_list[str(node)]) >= 1:
                connections = ', '.join(map(str, adj_list[str(node)]))
                print(f"{node} -> {connections}")
            else:
                print(node)

    def __str__(self):
        return f"Graph with {len(self.nodes)} nodes and {len(self.edges)} edges"

    def dump_nodes_json(self, nodes_json_path):
        nodes_json_list = []
        for node in self.nodes:
            nodes_json_list.append(node.to_json())
        
        with open(nodes_json_path, "w") as f:
            json.dump(nodes_json_list, f, indent=4)

    def dump_policy_edges_json(self, policy_edges_json_path):
        policy_edges_json_list = []
        for edge in self.edges:
            egde_json = edge.to_policy_json()
            if egde_json and (edge.source.scope != Scope.INVOCATION or edge.sink.scope != Scope.INVOCATION):
                policy_edges_json_list.append(egde_json)
        
        with open(policy_edges_json_path, "w") as f:
            json.dump(policy_edges_json_list, f, indent=4)
        logger.info(f"Policy spec generated at {policy_edges_json_path} with {len(policy_edges_json_list)}/{len(self.edges)} entries")