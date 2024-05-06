import uuid
from enum import Enum
from functools import partial

from src.utility import IDGenerator
from src.graph.policy.policy import EdgePolicy, generate_default_edge_policy
import json


class ReferenceType(Enum):
    """
    Enum class to define the type of reference.
    """

    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"


class InterfaceType(Enum):
    """
    Enum class to define the type of interface.
    """

    SOURCE = "SOURCE"
    SINK = "SINK"


class Scope(Enum):
    """
    Enum class to define the scope of the node.
    """

    CONTAINER = "CONTAINER"
    INVOCATION = "INVOCATION"
    GLOBAL = "GLOBAL"


class Reference:
    """
    Class to represent a reference.
    """

    def __init__(self, reference_type, reference_name):
        """
        Initialize a Reference instance.
        """
        self.reference_type: ReferenceType = reference_type
        self.reference_name: str = reference_name

    def __str__(self) -> str:
        """
        Return a string representation of the Reference instance.
        """
        return f"Reference({self.reference_type}:{self.reference_name})"

    def __repr__(self) -> str:
        return f"{self.reference_type}:{self.reference_name}"

    def __eq__(self, other):
        """
        Return True if the two references are equal.
        """
        return (
            self.reference_type == other.reference_type
            and self.reference_name == other.reference_name
        )


class Node:
    """
    Class to represent a node.
    """

    def __init__(
        self,
        resource_name: Reference,
        resource_type,
        data_object: Reference,
        scope: Scope,
        interface_type: InterfaceType,
        function,
        attributes=None,
    ):
        """
        Initialize a Node instance.
        """
        self.resource_id = "UNKNOWN"
        self.resource_name: Reference = resource_name
        self.resource_type = resource_type
        self.data_object: Reference = data_object
        self.interface_type: InterfaceType = (
            interface_type  # TODO: Remove this if we are collapsing graph nodes
        )
        self.scope: Scope = scope
        self.function = function
        self.attributes = attributes or {}
        # TODO: Quick add to check for policy eval
        self.attributes["PropDataObjectName"] = self.data_object
        self.uid = IDGenerator.get_id()

    @property
    def id(self):
        if self.resource_name.reference_type == ReferenceType.STATIC:
            return f"{self.function}:{self.resource_type}:{self.resource_name.reference_name}_{self.uid}"

        return f"{self.function}:{self.resource_type}:{{{self.resource_name.reference_name}}}_{self.uid}"

    def __str__(self):
        """
        Return a string representation of the Node instance.
        """
        return (
            f"Node(resource_id={self.resource_id}, resource_name={self.resource_name}, "
            f"resource_type={self.resource_type}, data_object={self.data_object}, "
            f"scope={self.scope}, function={self.function}, attributes={self.attributes})"
        )

    def __repr__(self):
        return f"{self.resource_type}:{self.resource_name.reference_name}.{self.data_object.reference_name}"

    # TODO: Should we add function in the id as well?
    @property
    def policy_id(self):
        return f"{self.resource_type}:{self.resource_name.reference_name}:{self.data_object.reference_name}"

    def __eq__(self, other):
        """
        Return True if the two nodes are equal.
        """
        if type(other) == str:
            return self.__repr__() == other
        return (
            self.resource_name == other.resource_name
            and self.resource_type == other.resource_type
            and self.resource_type == other.resource_type
            and self.data_object == other.data_object
            and self.scope == other.scope
            and self.function == other.function
        )


class DefaultNode(Node):
    """
    Special class for representing a default or placeholder node.
    """

    def __init__(self, function):
        super().__init__(
            Reference(ReferenceType.STATIC, "DEFAULT"),
            "DEFAULT",
            Reference(ReferenceType.STATIC, "DEFAULT"),
            Scope.INVOCATION,
            InterfaceType.SOURCE,
            function,
            attributes={},
        )


class Edge:
    """
    Class to represent an edge.
    """

    def __init__(
        self, source_node, sink_node, source_properties=None, sink_properties=None
    ):
        """
        Initialize an Edge instance.
        """
        self.source_node = source_node
        self.sink_node = sink_node
        self.source_properties = source_properties or {}
        self.sink_properties = sink_properties or {}
        self.edge_policy: EdgePolicy = None

    def __str__(self):
        """
        Return a string representation of the Edge instance.
        """
        return (
            f"Edge(source_node={self.source_node}, sink_node={self.sink_node}, "
            f"source_properties={self.source_properties}, sink_properties={self.sink_properties})"
        )

    def __repr__(self) -> str:
        return f"{self.source_node.__repr__()} -> {self.sink_node.__repr__()})"


class Graph:
    """
    Class to represent a graph.
    """

    def __init__(self):
        """
        Initialize a Graph instance.
        """
        self.nodes = []
        self.edges = []
        self.functions = set()

    def add_node(self, node):
        """
        Add a node to the graph.
        """
        self.nodes.append(node)

    def add_edge(self, edge):
        """
        Add an edge to the graph.
        """
        self.edges.append(edge)

    def add_function(self, function):
        """
        Add a function to the graph.
        """
        self.functions.add(function)

    def get_existing_or_add_node(self, new_node):
        # Check if a node with the same properties already exists in the graph
        for existing_node in self.nodes:
            if existing_node == new_node:
                return existing_node
        self.add_node(new_node)
        return new_node

    def __str__(self):
        """
        Return a string representation of the Graph instance.
        """
        return f"Graph(nodes={self.nodes}, edges={self.edges})"

    def get_sub_graph(self, function):
        """
        Return a subgraph for the specified function.
        """
        nodes = [node for node in self.nodes if node.function == function]
        edges = [
            edge
            for edge in self.edges
            if edge.source_node in nodes and edge.sink_node in nodes
        ]
        sub_graph = Graph()
        sub_graph.nodes = nodes
        sub_graph.edges = edges
        sub_graph.add_function(function)
        return sub_graph

    def apply_edges(self, apply_func, *args, **kwargs):
        """
        Apply the specified function to each edge in the graph.
        """
        for edge in self.edges:
            partial_apply_func = partial(apply_func, edge, *args, **kwargs)
            partial_apply_func()

    # def traverse(self, apply_func):
    #     visited = set()
    #     for node in self.nodes:
    #         # TODO: FIX Missing edges if started from intermediate node
    #         if node not in visited:
    #             visited.add(node)
    #             self.dfs_helper(node, visited, apply_func)

    # Store the accumulated policy json in a file
    def init_policies(self, policy_path):
        self.apply_edges(generate_default_edge_policy)
        edge_policies = []
        for edge in self.edges:
            if edge.edge_policy:
                edge_policies.append(edge.edge_policy.to_json())

        # Store the accumulated policy json in a file
        with open(policy_path, "w") as f:
            json.dump(edge_policies, f, indent=4)

    def append_policies(self, policy_path):
        edge_policies = json.load(open(policy_path))
        edge_policies = [EdgePolicy(policy) for policy in edge_policies]

        # remove the edge policies that are not in the graph anymore
        edge_policies = [
            edge_policy
            for edge_policy in edge_policies
            if self.edge_exists(edge_policy)
        ]

        edge_policy_map = {}

        for policy in edge_policies:
            edge_policy_map[
                (
                    policy.source_function,
                    policy.source,
                    policy.sink_function,
                    policy.sink,
                )
            ] = policy

        # add the edge policies that are new
        for edge in self.edges:
            if (
                edge.source_node.function,
                edge.source_node.policy_id,
                edge.sink_node.function,
                edge.sink_node.policy_id,
            ) not in edge_policy_map:
                default_policy = generate_default_edge_policy(edge)
                edge_policies.append(default_policy)

        # Store the accumulated policy json in a file
        with open(policy_path, "w") as f:
            json.dump([policy.to_json() for policy in edge_policies], f, indent=4)

    def edge_exists(self, edge_policy):
        for edge in self.edges:
            if (
                edge_policy.source_function == edge.source_node.function
                and edge_policy.source == edge.source_node.policy_id
                and edge_policy.sink_function == edge.sink_node.function
                and edge_policy.sink == edge.sink_node.policy_id
            ):
                return True
        return False
