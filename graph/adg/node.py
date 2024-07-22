from itertools import count

from graph.adg.types import Reference, ReferenceType, Scope, TaintLabelMatch
from .function import Function


class Node:
    _id_generator = count(0)

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
        self.node_id = next(self._id_generator)

        self.resource: Reference = resource
        self.resource_attrs = resource_attrs

        self.object: Reference = object
        self.object_type = object_type
        self.object_attrs = object_attrs

        self.object_handler = object_handler
        self.object_code_location = object_code_location
        self.object_fn: Function = object_fn
        self.scope: Scope = scope
        # Read/Write APIs?
        self.outgoing_edges = []
        self.incoming_edges = []

    def __str__(self):
        return f"({self.object_fn.name}:{self.resource}:{self.object})"

    def __repr__(self):
        # $ prefix denotes dynamic referece
        return f"{self.node_id}:{self.resource.__str__()}:{self.object.__str__()}"

    def __eq__(self, node2):
        """
        Return True if the two nodes are equal.
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
        return {
            "node_id": f"n{self.node_id}",
            "Resource": self.resource.__str__(),
            "ObjectType": self.object_type,
            "Object": self.object.__str__(),
            "Function": self.object_fn.path if self.object_fn else None,
        }

    @property
    def is_sink(self):
        return 'SINK' in self.object_code_location['message']['text']

    @property
    def is_source(self):
        return 'SOURCE' in self.object_code_location['message']['text']

