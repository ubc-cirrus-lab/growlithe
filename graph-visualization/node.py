from enum import Enum

class Node_Type(Enum):
    FUNCTION = 1
    RESOURCE = 2
    INTERNAL_SOURCE = 3
    INTERNAL_SINK = 3
    
class Security_Type(Enum):
    PUBLIC = 1
    PRIVATE = 2

# TODO: Add enum for endpoint type

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

    def __repr__(self):
        if self.parent_function is not None:
            return f"{self.name} (Parent: {self.parent_function.name})"
        return self.name
    
    def add_child(self, child):
        self.children.append(child)
