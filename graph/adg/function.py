import os
import ast

from common.app_config import app_path
from .resource import Resource

"""
Stores all functions in a given application, their dependencies and nodes/edges corresponding to them
"""


class Function(Resource):
    def __init__(self, name, type, runtime, path, metadata=dict()):
        super(Function, self).__init__(name, type, metadata)
        self.path: str = path
        self.runtime = runtime

        self.sarif_results = None
        self.event_node = None
        self.return_node = None
        self.nodes = []
        self.edges = []

        # TODO: Make this language agnostic
        if self.path:
            self.file = os.path.join(path, 'app.py')
            with open(f"{app_path}/{self.file}", "r") as f:
                code = f.read()
                tree = ast.parse(code)
                self.code_tree = tree

    def __str__(self):
        pass

    def __repr__(self):
        return f"{self.name} ({self.path})"

    def add_node(self, node):
        self.nodes.append(node)

    def add_sarif_results(self, results):
        self.sarif_results = results

    def add_event_node(self, node):
        self.event_node = node
    
    def add_return_node(self, node):
        self.return_node = node

    def get_event_node(self):
        return self.event_node

    def get_return_node(self):
        return self.return_node
