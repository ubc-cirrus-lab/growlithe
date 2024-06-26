from enum import Enum


class ReferenceType(Enum):
    """
    Enum class to define the type of reference.
    """

    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"


class InterfaceType(Enum):
    """
    Enum class to define the type of interface.
    """

    SOURCE = "SOURCE"
    SINK = "SINK"


class Scope(Enum):
    """
    Enum class to define the scope of the node.
    """

    CONTAINER = "CONTAINER"
    INVOCATION = "INVOCATION"
    GLOBAL = "GLOBAL"


class Reference:
    """
    Class to represent a reference.
    """

    def __init__(self, reference_type, reference_name):
        """
        Initialize a Reference instance.
        """
        self.reference_type: ReferenceType = reference_type
        self.reference_name: str = reference_name

    def __str__(self) -> str:
        """
        Return a string representation of the Reference instance.
        """
        return f"{'$' if self.reference_type == ReferenceType.DYNAMIC else ''}{self.reference_name}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other):
        """
        Return True if the two references are equal.
        """
        return (
            self.reference_type == other.reference_type
            and self.reference_name == other.reference_name
        )

class TaintLabelMatch(Enum):
    """
    Enum class to define possible taint label matches.
    """

    MATCH = "MATCH"
    POSSIBLE_MATCH = "POSSIBLE_MATCH"
    NO_MATCH = "NO_MATCH"
