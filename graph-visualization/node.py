from enum import Enum

class Node_Type(Enum):
    FUNCTION = 1
    RESOURCE = 2
    INTERNAL_SOURCE = 3
    INTERNAL_SINK = 3
    
class Security_Type(Enum):
    PUBLIC = 1
    PRIVATE = 2

class Endpoint_Type(Enum):
    PARAM = 1
    BOTO3 = 2
    FILE = 3
    RETURN = 4

class Node:
    def __init__(self, name):
        self.name = name
        # Direct edges to
        self.children = []
        # Internal nodes
        self.internal = []
        self.type = None
        self.endpoint_type = None
        self.parent_function = None
        self.physicalLocation = None
        self.security_type = Security_Type.PUBLIC

    def __repr__(self):
        if self.parent_function is not None:
            return f"{self.name} {'[Private]' if self.security_type == Security_Type.PRIVATE else ''} (Parent: {self.parent_function.name})"
        return self.name
    
    def add_child(self, child):
        self.children.append(child)
