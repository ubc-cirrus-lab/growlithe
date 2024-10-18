"""
Module for representing and manipulating Application Dependency Graphs (ADG).

This module provides the Graph class, which is the core data structure for
representing the relationships between nodes, edges, functions, and resources
in an application.
"""

import json
import ast
from collections import deque
from typing import List
from growlithe.common.logger import logger
from growlithe.common.utils import profiler_decorator
from growlithe.graph.adg.node import Node
from growlithe.graph.adg.edge import Edge, EdgeType
from growlithe.graph.adg.function import Function
from growlithe.graph.adg.resource import Resource
from growlithe.graph.adg.types import Scope


class Graph:
    """
    Represents an Application Dependency Graph (ADG).

    This class manages the nodes, edges, functions, and resources that make up
    the graph structure of an application.
    """

    def __init__(self, name: str = ""):
        self.name: str = name  # Name of the graph
        self.nodes: List[Node] = []  # List of all nodes in the graph
        self.edges: List[Edge] = []  # List of all edges in the graph
        self.reverse_edges: List[Edge] = []  # List of reverse edges
        self.metadata_edges: List[Edge] = []  # List of metadata edges

        self.functions: List[Function] = []  # List of functions in the graph
        self.resources: List[Resource] = []  # List of resources in the graph

    def add_node(self, new_node: Node):
        """
        Add a new node to the graph if it doesn't already exist.

        Args:
            new_node (Node): The node to be added.

        Returns:
            Node: The added node or an existing equivalent node.
        """
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
        """
        Add a new edge to the graph if it doesn't already exist.

        Args:
            edge (Edge): The edge to be added.

        Returns:
            Edge: The added edge or an existing equivalent edge.
        """
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

    def add_functions(self, functions: list[Function]):
        """
        Add a list of functions to the graph.

        Args:
            functions (list[Function]): The functions to be added.
        """
        self.functions = functions

    def add_resources(self, resources: list[Resource]):
        """
        Add a list of resources to the graph.

        Args:
            resources (list[Resource]): The resources to be added.
        """
        self.resources = resources

    def visualize(self):
        """
        Visualize the graph structure by printing node connections.
        """
        adj_list = {str(node): [] for node in self.nodes}
        for edge in self.edges:
            adj_list[str(edge.source)].append(edge.sink)

        for node in self.nodes:
            if len(adj_list[str(node)]) >= 1:
                connections = ", ".join(map(str, adj_list[str(node)]))
                print(f"{node} -> {connections}")
            else:
                print(node)

    def __str__(self):
        """
        Return a string representation of the graph.

        Returns:
            str: A string describing the number of nodes and edges in the graph.
        """
        return f"Graph with {len(self.nodes)} nodes and {len(self.edges)} edges"

    def dump_nodes_json(self, nodes_json_path):
        """
        Dump the graph nodes to a JSON file.

        Args:
            nodes_json_path (str): The path to save the JSON file.
        """
        nodes_json_list = []
        for node in self.nodes:
            nodes_json_list.append(node.to_json())

        with open(nodes_json_path, "w") as f:
            json.dump(nodes_json_list, f, indent=4)

    def dump_policy_edges_json(self, policy_edges_json_path):
        """
        Dump the policy edges to a JSON file.

        Args:
            policy_edges_json_path (str): The path to save the JSON file.
        """
        policy_edges_json_list = []
        for edge in self.edges:
            egde_json = edge.to_policy_json()
            if egde_json and (
                edge.source.scope != Scope.INVOCATION
                or edge.sink.scope != Scope.INVOCATION
            ):
                policy_edges_json_list.append(egde_json)

        with open(policy_edges_json_path, "w") as f:
            json.dump(policy_edges_json_list, f, indent=4)
        logger.info(
            f"Policy spec generated at {policy_edges_json_path} with {len(policy_edges_json_list)}/{len(self.edges)} entries"
        )

    @profiler_decorator
    def get_updated_policy_json(self, policy_edges_json_path):
        """
        Update the graph edges with policy information from a JSON file.

        Args:
            policy_edges_json_path (str): The path to the policy JSON file.
        """
        with open(policy_edges_json_path, "r") as f:
            policy_edges = json.load(f)

        for policy_edge in policy_edges:
            self.update_edge(policy_edge, self.edges)

    @staticmethod
    def update_edge(policy_edge, edges):
        """
        Update a single edge with policy information.

        Args:
            policy_edge (dict): Policy information for the edge.
            edges (list): List of edges to update.
        """
        edge_id = policy_edge["id"]
        edges[edge_id].update_policy(policy_edge)

    def insert_assertion(self, node: Node, assertion, code_path=None, tree=None):
        """
        Insert an assertion into the AST of a function.

        Args:
            node (Node): The node where the assertion should be inserted.
            assertion (str): The assertion to be inserted.
            code_path (dict, optional): The code location information.
            tree (ast.AST, optional): The AST to modify.
        """
        if tree is None:
            tree = node.object_fn.code_tree
        if code_path is None:
            code_path = node.object_code_location
        start_line = code_path["physicalLocation"]["region"]["startLine"]
        end_line = code_path["physicalLocation"]["region"].get("endLine", start_line)
        if getattr(tree, "body", None):
            for i, ast_node in enumerate(tree.body):
                if (
                    getattr(ast_node, "lineno", None) == start_line
                    and getattr(ast_node, "end_lineno", None) == end_line
                ):
                    tree.body.insert(i, ast.parse(assertion))
                    return
                self.insert_assertion(node, assertion, code_path, ast_node)

    @profiler_decorator
    def enforce_policy(self):
        """
        Enforce policies by inserting assertions into the code.
        """
        self.populate_ancestors()
        for edge in self.edges:
            # TODO: Add to the instrumented code
            read_assertion = edge.read_policy.generate_assertion(edge.function.runtime)
            if read_assertion:
                logger.debug(
                    f"Adding assertion in {edge.function.function_path}:\n {read_assertion}"
                )
                self.insert_assertion(edge.source, read_assertion)

            write_assertion = edge.write_policy.generate_assertion(
                edge.function.runtime
            )
            if write_assertion:
                logger.debug(
                    f"Adding assertion in {edge.function.function_path}:\n {write_assertion}"
                )
                self.insert_assertion(edge.sink, write_assertion)

    def populate_ancestors(self):
        """
        Populate ancestor information for each node in the graph.

        This method performs a topological sort to determine the ancestor
        relationships between nodes and functions in the graph.

        Time Complexity: O(V + E), where V is the number of nodes and E is the number of edges.
        """
        # Calculate in-degree for each node, i.e. number of incoming edges for each sink node
        in_degree = {node: 0 for node in self.nodes}
        for edge in self.edges:
            in_degree[edge.sink] += 1

        # Initialize queue with nodes having in-degree 0
        queue = deque([node for node in self.nodes if in_degree[node] == 0])

        # Process nodes in topological order, i.e. increasing order of in-degree
        while queue:
            current_node = queue.popleft()

            # Add current node's function to its ancestor_functions
            current_node.ancestor_functions.add(current_node.object_fn)

            # Process outgoing edges
            for edge in current_node.outgoing_edges:
                child_node = edge.sink

                # Add current node and its ancestors to child's ancestors
                child_node.ancestor_nodes.add(current_node)
                child_node.ancestor_nodes.update(current_node.ancestor_nodes)

                # Add current node's function and ancestor functions to child's ancestor functions
                child_node.ancestor_functions.add(current_node.object_fn)
                child_node.ancestor_functions.update(current_node.ancestor_functions)

                # Decrease in-degree of child node
                in_degree[child_node] -= 1
                if in_degree[child_node] == 0:
                    queue.append(child_node)

        # Check for cycles
        if sum(in_degree.values()) > 0:
            logger.warning("ADG contains possible cycles.")
