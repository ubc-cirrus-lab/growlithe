import uuid
from enum import Enum

from src.graph.policy.policy import EdgePolicy
from src.utility import IDGenerator


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
        return f"{self.function}:{self.resource_type}:{self.resource_name.reference_name}_{self.uid}"

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
        return f"{self.resource_type}:{self.resource_name.reference_name}"

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

    def apply_edges(self, apply_func):
        """
        Apply the specified function to each edge in the graph.
        """
        for edge in self.edges:
            apply_func(edge)
