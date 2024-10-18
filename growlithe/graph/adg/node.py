"""
Module for representing nodes in an Application Dependency Graph (ADG).

This module defines the Node class, which represents individual elements
in the graph structure of an application.
"""

from itertools import count

from growlithe.graph.adg.resource import Resource
from growlithe.graph.adg.types import Reference, ReferenceType, Scope, TaintLabelMatch
from growlithe.graph.adg.function import Function


class Node:
    """
    Represents a node in the Application Dependency Graph (ADG).

    This class encapsulates the properties and relationships of individual
    elements within the graph structure.
    """

    _id_generator = count(0)  # Generator for unique node IDs

    def __init__(
        self,
        resource: Reference,
        object: Reference,
        object_type: str,
        object_handler: str,
        object_code_location,
        object_fn: Function,
        object_attrs: dict,
        resource_attrs: dict,
        scope: Scope,
    ):
        """
        Initialize a Node instance.

        Args:
            resource (Reference): Reference to the resource associated with this node.
            object (Reference): Reference to the object represented by this node.
            object_type (str): Type of the object.
            object_handler (str): Handler for the object.
            object_code_location: Code location information for the object.
            object_fn (Function): Function associated with this node.
            object_attrs (dict): Additional attributes of the object.
            resource_attrs (dict): Additional attributes of the resource.
            scope (Scope): Scope of the node.
        """
        self.node_id = next(self._id_generator)  # Unique identifier for the node

        self.resource: Reference = resource  # Reference to the associated resource
        self.resource_attrs = resource_attrs  # Additional resource attributes

        self.object: Reference = object  # Reference to the object
        self.object_type = object_type  # Type of the object
        self.object_attrs = object_attrs  # Additional object attributes

        self.object_handler = object_handler  # Handler for the object
        self.object_code_location = object_code_location  # Code location of the object
        self.object_fn: Function = object_fn  # Associated function
        self.scope: Scope = scope  # Scope of the node
        self.mapped_resource: Resource = None  # Mapped resource (if any)

        self.outgoing_edges = []  # List of outgoing edges
        self.incoming_edges = []  # List of incoming edges

        # Upstream nodes and functions in the ADG for a given node
        # Function of the current node will be included in the list
        self.ancestor_nodes = set()  # Set of ancestor nodes
        self.ancestor_functions = set()  # Set of ancestor functions

    def __hash__(self):
        """
        Generate a hash for the node based on its unique ID.

        Returns:
            int: Hash value of the node.
        """
        return hash(self.node_id)

    def __str__(self):
        """
        Return a string representation of the node.

        Returns:
            str: String representation of the node.
        """
        return f"({self.object_fn.name}:{self.resource}:{self.object})"

    def __repr__(self):
        """
        Return a detailed string representation of the node.

        Returns:
            str: Detailed string representation of the node.
        """
        # $ prefix denotes dynamic reference
        return f"{self.node_id}:{self.resource.__str__()}:{self.object.__str__()}"

    def __eq__(self, node2):
        """
        Check if two nodes are equal.

        Args:
            node2: Another node or string to compare with.

        Returns:
            bool: True if the nodes are equal, False otherwise.
        """
        if type(node2) == str:
            return self.__repr__() == node2
        return (
            self.resource == node2.resource
            and self.object_type == node2.object_type
            and self.object == node2.object
            and self.object_fn == node2.object_fn
            and self.scope == node2.scope
        )

    def to_json(self):
        """
        Convert the node to a JSON-serializable dictionary.

        Returns:
            dict: JSON representation of the node.
        """
        return {
            "node_id": f"n{self.node_id}",
            "Resource": self.resource.__str__(),
            "ObjectType": self.object_type,
            "Object": self.object.__str__(),
            "Function": self.object_fn.function_path if self.object_fn else None,
        }

    @property
    def is_sink(self):
        """
        Check if the node is a sink.

        Returns:
            bool: True if the node is a sink, False otherwise.
        """
        return "SINK" in self.object_code_location["message"]["text"]

    @property
    def is_source(self):
        """
        Check if the node is a source.

        Returns:
            bool: True if the node is a source, False otherwise.
        """
        return "SOURCE" in self.object_code_location["message"]["text"]
