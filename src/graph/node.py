from enum import Enum
from typing import Tuple, Set


# Represents if data flows from or through a given container node
class DataflowType(Enum):
    SOURCE = 1
    SINK = 2


class SecurityType(Enum):
    PUBLIC = 1
    PRIVATE = 2
    UNKNOWN = 3


class BroadType(Enum):
    IDH_PARAM = 1
    IDH_OTHER = 2
    COMPUTE = 3
    RESOURCE = 4


class NodeType(Enum):
    (
        FUNCTION,
        PARAMETER,
        RETURN,
        S3_BUCKET,
        DYNAMODB_TABLE,
        LOCAL_FILE,
        SNS_TOPIC,
        SQS_QUEUE,
    ) = range(8)

    def __str__(self):
        return self.name


class Node:
    def __init__(self, name):
        self.name = name  # Name of the node
        self.edges: set[Node] = set()  # Set of nodes that this node has an edge to
        self.children: set[Node] = set()  # Set of internal nodes
        self.parents: set[Node] = set()  # Set of parent nodes TODO: Check if we need multiple parents
        # self.securityDependencies: set(Node) = set() # Set of nodes that this node depends on for its security label

        self.dataflow_type: DataflowType = None
        self.node_type: NodeType = None
        self.parent_function_node: Node = None  # The function node that this node is an internal node of
        self.physical_location = None
        self.security_type = SecurityType.UNKNOWN
        self.file_path = None

        self.attributes = {}
        self.missing_attributes = set()
        self.conditions: Set[Tuple[bool, str]] = set()

    def __repr__(self):
        result = f"Node({self.name})"
        return result

    def __str__(self):
        return f"{self.name} (Type: {self.node_type})"

    # Has no hierarchy
    def is_root_node(self):
        return self.node_type in [NodeType.FUNCTION, NodeType.PARAMETER, NodeType.RETURN]

    def add_edge(self, node):
        self.edges.add(node)

    def add_child(self, node):
        self.children.add(node)

    def add_parent(self, node):
        self.parents.add(node)

    @property
    def broad_node_type(self):
        if self.node_type == NodeType.PARAMETER:
            return BroadType.IDH_PARAM
        elif self.node_type == NodeType.FUNCTION:
            return BroadType.COMPUTE
        # elif self.nodeType == NodeType.RETURN:
        #     return BroadType.IDH_OTHER
        # Handlers for resources
        elif self.parent_function_node is not None:
            return BroadType.IDH_OTHER
        else:
            return BroadType.RESOURCE

    @property
    def policy_str(self):
        return f"{self.broad_node_type.name}/{self.name}"

    def is_idh(self):
        return self.node_type == NodeType.PARAMETER

    def is_compute(self):
        return self.node_type == NodeType.FUNCTION

    def is_resource(self):
        return self.node_type not in [NodeType.PARAMETER, NodeType.FUNCTION, NodeType.RETURN]
