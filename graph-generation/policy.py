from node import Node
from enum import Enum
from typing import Tuple, Set, List

class PERM(Enum):
    READ = 1
    WRITE = 2
    EXECUTE = 3

class Policy:
    def __init__(self, subject, object, perm):
        # Missing subject, object, perm means deny
        self.subject: Node = subject
        self.object: Node = object
        self.perm: PERM = perm

        # OR Separated policy groups, empty set means allow
        self.policyGroups: set(PolicyGroup) = set()
    
    def __repr__(self):
        return f"{self.subject.name} can {self.perm} {self.object.name} with conditions {self.policyGroups}"

class PolicyGroup:
    def __init__(self, allow_filters) -> None:
        # AND Separated filters as typle of (function, params_array)
        self.allow_filters: Set(Tuple(function, List)) = set(allow_filters)

class AllowFilters:
    def isEndUser(self, var_end_user, end_user):
        return var_end_user == end_user
