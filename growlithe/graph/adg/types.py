"""
Module for defining types and references used in the Application Dependency Graph (ADG).

This module contains enum classes for various types and a Reference class
to represent references within the application structure.
"""

from enum import Enum


class ReferenceType(Enum):
    """
    Enum class to define the type of reference.

    Attributes:
        STATIC: Represents a static reference.
        DYNAMIC: Represents a dynamic reference.
    """

    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"


class InterfaceType(Enum):
    """
    Enum class to define the type of interface.

    Attributes:
        SOURCE: Represents a source interface.
        SINK: Represents a sink interface.
    """

    SOURCE = "SOURCE"
    SINK = "SINK"


class Scope(Enum):
    """
    Enum class to define the scope of the node.

    Attributes:
        CONTAINER: Represents container scope.
        INVOCATION: Represents invocation scope.
        GLOBAL: Represents global scope.
    """

    CONTAINER = "CONTAINER"
    INVOCATION = "INVOCATION"
    GLOBAL = "GLOBAL"


class Reference:
    """
    Class to represent a reference in the Application Dependency Graph.
    """

    def __init__(self, reference_type: ReferenceType, reference_name: str):
        """
        Initialize a Reference instance.

        Args:
            reference_type (ReferenceType): The type of the reference (STATIC or DYNAMIC).
            reference_name (str): The name of the reference.
        """
        self.reference_type: ReferenceType = reference_type
        self.reference_name: str = reference_name

    def __str__(self) -> str:
        """
        Return a string representation of the Reference instance.

        Returns:
            str: String representation of the reference, prefixed with '$' for dynamic references.
        """
        return f"{'$' if self.reference_type == ReferenceType.DYNAMIC else ''}{self.reference_name}"

    def __repr__(self) -> str:
        """
        Return a string representation of the Reference instance for debugging.

        Returns:
            str: Same as __str__ method.
        """
        return self.__str__()

    def __eq__(self, other):
        """
        Check if two Reference instances are equal.

        Args:
            other (Reference): Another Reference instance to compare with.

        Returns:
            bool: True if both references have the same type and name, False otherwise.
        """
        return (
            self.reference_type == other.reference_type
            and self.reference_name == other.reference_name
        )


class TaintLabelMatch(Enum):
    """
    Enum class to define possible taint label matches.

    Attributes:
        MATCH: Represents a definite match.
        POSSIBLE_MATCH: Represents a possible match.
        NO_MATCH: Represents no match.
    """

    MATCH = "MATCH"
    POSSIBLE_MATCH = "POSSIBLE_MATCH"
    NO_MATCH = "NO_MATCH"
