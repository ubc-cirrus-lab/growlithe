"""
Module for representing functions in an Application Dependency Graph (ADG).

This module defines the Function class, which stores information about individual
functions in an application, including their dependencies, nodes, and edges.
"""

import os
import ast
import json
import subprocess

from growlithe.common.logger import logger
from growlithe.graph.adg.resource import Resource


class Function(Resource):
    """
    Represents a function in the Application Dependency Graph (ADG).

    This class extends the Resource class and encapsulates additional properties
    and methods specific to functions in the application.
    """

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
        """
        Initialize a Function instance.

        Args:
            name (str): Name of the function.
            type (str): Type of the function.
            runtime (str): Runtime environment of the function.
            function_path (str): Path to the function's source code.
            growlithe_function_path (str): Path to the Growlithe-specific function file.
            metadata (dict, optional): Additional metadata for the function. Defaults to an empty dict.
            deployed_region (str, optional): Region where the function is deployed. Defaults to None.
        """
        super(Function, self).__init__(name, type, metadata, deployed_region)
        self.function_path: str = function_path  # Path to the function's source code
        self.growlithe_function_path: str = (
            growlithe_function_path  # Path to Growlithe-specific function file
        )
        self.runtime = runtime  # Runtime environment of the function

        self.sarif_results = None  # SARIF analysis results
        self.event_node = None  # Event node associated with the function
        self.return_node = None  # Return node associated with the function
        self.nodes = []  # List of nodes in the function
        self.edges = []  # List of edges in the function
        self.iam_policies = []  # List of IAM policies associated with the function
        self.code_tree = None  # AST of the function's code

        if self.function_path:
            if "python" in self.runtime:
                with open(function_path, "r") as f:
                    code = f.read()
                    tree = ast.parse(code)
                    self.code_tree = tree
            elif "nodejs" in self.runtime:
                subprocess.run(
                    [
                        "node",
                        "growlithe/graph/adg/js/file2ast.js",
                        self.function_path,
                    ],
                    check=True,
                )
                with open("tmp.json", encoding="utf-8") as f:
                    self.code_tree = json.load(f)
                os.remove("tmp.json")
                # raise NotImplementedError
            else:
                raise NotImplementedError
        else:
            logger.error("Path for function %s is empty.", self.name)
            raise FileNotFoundError

    def __str__(self):
        """
        Return a string representation of the function.

        Returns:
            str: String representation of the function.
        """
        return self.__repr__()

    def __repr__(self):
        """
        Return a detailed string representation of the function.

        Returns:
            str: Detailed string representation of the function.
        """
        return f"{self.name} ({self.function_path})"

    def add_node(self, node):
        """
        Add a node to the function's list of nodes.

        Args:
            node: The node to be added.
        """
        self.nodes.append(node)

    def add_sarif_results(self, results):
        """
        Add SARIF analysis results to the function.

        Args:
            results: The SARIF analysis results to be added.
        """
        self.sarif_results = results

    def add_event_node(self, node):
        """
        Set the event node for the function.

        Args:
            node: The event node to be set.
        """
        self.event_node = node

    def add_return_node(self, node):
        """
        Set the return node for the function.

        Args:
            node: The return node to be set.
        """
        self.return_node = node

    def get_event_node(self):
        """
        Get the event node of the function.

        Returns:
            The event node of the function.
        """
        return self.event_node

    def get_return_node(self):
        """
        Get the return node of the function.

        Returns:
            The return node of the function.
        """
        return self.return_node
