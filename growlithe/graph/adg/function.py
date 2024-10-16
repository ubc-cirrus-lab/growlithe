import ast

from growlithe.common.logger import logger
from growlithe.graph.adg.resource import Resource


"""
Stores all functions in a given application, their dependencies and nodes/edges corresponding to them
"""


class Function(Resource):
    def __init__(
        self,
        name,
        type,
        runtime,
        function_path,
        growlithe_function_path,
        metadata=dict(),
        deployed_region=None,
    ):
        super(Function, self).__init__(name, type, metadata, deployed_region)
        self.function_path: str = function_path
        self.growlithe_function_path: str = growlithe_function_path
        self.runtime = runtime

        self.sarif_results = None
        self.event_node = None
        self.return_node = None
        self.nodes = []
        self.edges = []
        self.iam_policies = []
        self.code_tree = None

        if self.function_path:
            if "python" in self.runtime:
                with open(function_path, "r") as f:
                    code = f.read()
                    tree = ast.parse(code)
                    self.code_tree = tree
            elif "nodejs" in self.runtime:
                logger.error(f"NodeJS runtime is not supported yet.")
                # raise NotImplementedError
            else:
                raise NotImplementedError
        else:
            logger.error(f"Path for function {self.name} is empty.")
            raise FileNotFoundError

    def __str__(self):
        self.__repr__()

    def __repr__(self):
        return f"{self.name} ({self.function_path})"

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
