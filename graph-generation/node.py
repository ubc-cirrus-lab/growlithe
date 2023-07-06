from enum import Enum
import uuid

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
        LOCAL_FILE,
        SNS_TOPIC,
        SQS_QUEUE,
    ) = range(7)


class Node:
    def __init__(self, name):
        self.name = name  # Name of the node
        self.edges: set(Node) = set()  # Set of nodes that this node has an edge to
        self.children: set(Node) = set()  # Set of internal nodes
        self.parents: set(Node) = set()  # Set of parent nodes TODO: Check if we need multiple parents
        # self.securityDependencies: set(Node) = set() # Set of nodes that this node depends on for it's security label

        self.dataflowType: DataflowType = None
        self.nodeType: NodeType = None
        self.parentFunctionNode: Node = None # The function node that this node is an internal node of
        self.physicalLocation = None
        self.securityType = SecurityType.UNKNOWN


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

    def get_broad_node_type(self):
        if self.nodeType == NodeType.PARAMETER:
            return BroadType.IDH_PARAM
        elif self.nodeType == NodeType.FUNCTION:
            return BroadType.COMPUTE
        # elif self.nodeType == NodeType.RETURN:
        #     return BroadType.IDH_OTHER
        # Handlers for resources
        elif self.parentFunctionNode is not None:
            return BroadType.IDH_OTHER
        else:
            return BroadType.RESOURCE

    def is_idh(self):
        return self.nodeType == NodeType.PARAMETER

    def is_compute(self):
        return self.nodeType == NodeType.FUNCTION

    def is_resource(self):
        return self.nodeType not in [NodeType.PARAMETER, NodeType.FUNCTION, NodeType.RETURN]
