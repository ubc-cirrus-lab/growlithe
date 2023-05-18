from enum import Enum


class Node_Type(Enum):
    FUNCTION = 1
    RESOURCE = 2


class Node:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.type = None
        self.parent_function = None

    def add_child(self, child):
        self.children.append(child)
