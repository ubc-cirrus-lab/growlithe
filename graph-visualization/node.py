from enum import Enum
import uuid

# Represents if data flows from or through a given container node
class DataflowType(Enum):
    SOURCE = 1
    SINK = 2


class SecurityType(Enum):
    PUBLIC = 1
    PRIVATE = 2


class NodeType(Enum):
    (
        FUNCTION,
        PARAMETER,
        S3_BUCKET,
        LOCAL_FILE,
        RETURN,
        SNS_TOPIC,
        SQS_QUEUE,
    ) = range(7)


class Node:
    def __init__(self, name):
        self.name = name  # Name of the node
        self.edges: set(Node) = set()  # Set of nodes that this node has an edge to
        self.children: set(Node) = set()  # Set of internal nodes
        self.parents: set(Node) = set()  # Set of parent nodes TODO: Check if we need multiple parents

        self.dataflowType: DataflowType = None
        self.nodeType: NodeType = None
        self.parentFunctionNode: Node = None # The function node that this node is an internal node of
        self.physicalLocation = None
        self.securityType = SecurityType.PUBLIC


    def __repr__(self):
        result = f"{self.name} {'[Private]' if self.securityType == SecurityType.PRIVATE else ''}"
        if self.parentFunctionNode is not None:
            result += f"(ParentFunc: {self.parentFunctionNode.name})"
        if self.parents is not None:
            result += f"(Parents: {self.parents})"
        return result

    # Has no hierarchy
    def is_root_node(self):
        return self.nodeType in [NodeType.FUNCTION, NodeType.PARAMETER, NodeType.RETURN]

    def add_edge(self, node):
        self.edges.add(node)
    
    def add_child(self, node):
        self.children.add(node)

    def add_parent(self, node):
        self.parents.add(node)