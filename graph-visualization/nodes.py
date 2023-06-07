from enum import Enum

class Security_Type(Enum):
    PUBLIC = 1
    PRIVATE = 2

# class NodeClass(Enum):
class Node:
    def __init__(self, name):
        self.name = name
        self.children = set()
        self.internal = []
        self.security_type = Security_Type.PUBLIC

class OuterNode(Node):
    def __init__(self, name):
        super().__init__(name)
        self.type = "OuterNode"

class InnerNode(Node):
    def __init__(self, name):
        super().__init__(name)
        self.type = "InnerNode"