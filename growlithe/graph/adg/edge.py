"""
Module for representing edges in the Application Dependency Graph (ADG).

This module defines the Edge class, which stores information about individual
edges in the ADG, along with type of the edge.
"""

from enum import Enum
from growlithe.enforcement.policy.policy_enforcer import Policy
from growlithe.graph.adg.function import Function
from growlithe.graph.adg.node import Node
from itertools import count
from growlithe.common.dev_config import DEFAULT_POLICY

class EdgeType(Enum):
    """
    Enum class to define the type of edge.
    """

    DATA = "DATA"
    METADATA = "METADATA"
    INDIRECT = "INDIRECT"


class Edge:
    _id_generator = count(0)

    def __init__(
        self,
        u: Node,
        v: Node,
        source_code_path,
        sink_code_path,
        function: Function,
        edge_type: EdgeType,
    ):
        self.source: Node = u
        self.sink: Node = v
        self.source_code_path = source_code_path
        self.sink_code_path = sink_code_path
        self.function: Function = function
        self.edge_type: EdgeType = edge_type
        self.edge_id = next(self._id_generator)

        # Default Policies
        self.read_policy = Policy("READ", DEFAULT_POLICY)
        self.write_policy = Policy("WRITE", DEFAULT_POLICY)

    def __repr__(self):
        return f"{self.source.__repr__()} -{self.edge_id}-> {self.sink.__repr__()}"

    def __eq__(self, edge2):
        """
        Return True if the two edges are equal.
        """
        return (
            self.source == edge2.source
            and self.sink == edge2.sink
            and self.edge_type == edge2.edge_type
        )

    def to_policy_json(self):
        if self.edge_type == EdgeType.DATA:
            return {
                "id": self.edge_id,
                "source": self.source.__repr__(),
                "sink": self.sink.__repr__(),
                "read": self.read_policy.__str__(),
                "write": self.write_policy.__str__(),
                "function": self.function.__repr__(),
            }
        return None

    def update_policy(self, policy_json):
        self.read_policy = Policy("READ", policy_json["read"], self.source)
        self.write_policy = Policy("WRITE", policy_json["write"], self.sink)
