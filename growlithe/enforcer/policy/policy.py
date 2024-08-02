from __future__ import annotations
import re
from typing import List, Set
from growlithe.common import logger
from growlithe.common.tasks_config import HYBRID_ENFORCEMENT_MODE
from growlithe.enforcer.policy.template.growlithe import *
from growlithe.enforcer.taint.taint_utils import online_taint_label
from growlithe.graph.adg.node import Node
from growlithe.graph.adg.types import ReferenceType


class PolicyPredicate:
    """AND separated policy predicate in a DNF policy clause"""

    def __init__(self, predicate_str: str):
        self.predicate_str = predicate_str.strip()
        self.predicate_name, self.arguments = self.parse_predicate()
        # Datalog variables used in the predicate
        self.variables = self.extract_variables()
        self.predicate_name

    def parse_predicate(self):
        match = re.match(r"(\w+)\s*\((.*)\)$", self.predicate_str)
        if match:
            name = match.group(1)
            args = [arg.strip() for arg in match.group(2).split(",")]
            return name, args
        else:
            logger.error(f"Error: '{self.predicate_str}' is not a valid function predicate")
            return "", []

    def extract_variables(self) -> Set[str]:
        variables = set()
        for arg in self.arguments:
            # If the argument is not a string literal or a number, consider it a variable
            if not (arg.startswith(("'", '"')) or arg.replace(".", "").isdigit()):
                variables.add(arg)
        return variables


class PredicateSet:
    def __init__(self, predicates: Set[PolicyPredicate]):
        self.predicates: Set[PolicyPredicate] = predicates
        self.variables = self.extract_variables()

    def extract_variables(self) -> Set[str]:
        variables = set()
        for pred in self.predicates:
            variables.update(pred.variables)
        return variables

    @property
    def contains_session_variables(self) -> bool:
        return any(var.startswith("Session") for var in self.variables)

    def add_predicate(self, predicate: PolicyPredicate):
        self.predicates.add(predicate)

    @property
    def query(self) -> str:
        return " & ".join([f"{pred.predicate_str}" for pred in self.predicates])

    @property
    def deferred_query(self):
        if self.contains_session_variables:
            return self.query
        try:
            if pyDatalog.ask(self.query) == None:
                logger.error(f"OFFLINE POLICY ERROR: Partial policy failed offline check: {self.query}")
            else:
                # FIXME: Complete pipeline when offline checks are successful
                return None
        except Exception as e:
            return self.query


class PolicyClause:
    """OR separated policy clause in a DNF policy"""

    def __init__(self, predicates: List[PolicyPredicate], policy: Policy):
        self.predicates: List[PolicyPredicate] = predicates
        self.disjoint_predicates: List[PredicateSet] = self.divide_into_disjoint_sets()
        self.policy = policy
        self.insert_implicit_predicate()

    # # Each clause can have set of predicates that can be evaluated independently of the other predicates
    def divide_into_disjoint_sets(self) -> List[PredicateSet]:
        disjoint_sets: List[PredicateSet] = []
        predicates: List[PolicyPredicate] = self.predicates.copy()
        while predicates:
            predicate = predicates.pop(0)
            current_set: Set[PolicyPredicate] = {predicate}
            current_vars = set(predicate.variables)

            i = 0
            while i < len(predicates):
                if current_vars & set(predicates[i].variables):
                    current_predicate = predicates.pop(i)
                    current_set.add(current_predicate)
                    current_vars.update(current_predicate.variables)
                else:
                    i += 1

            disjoint_sets.append(PredicateSet(current_set))

        return disjoint_sets

    def insert_implicit_predicate(self):
        for disjoint_set in self.disjoint_predicates:
            # TODO: Replace with properties stored in node/edge objects
            # Resolve growlithe identifiers
            for var in disjoint_set.variables:
                if var.startswith("Session"):
                    raise NotImplementedError("Session variables not supported yet")
                elif var.startswith("Inst"):
                    # Instance properties only resolved at runtime
                    disjoint_set.add_predicate(
                        PolicyPredicate(f"eq({var}, '{{getInstProp('{var}')}}')")
                    )
                elif var.startswith("Resource"):  # Try to resolve identifier offline
                    if (
                        HYBRID_ENFORCEMENT_MODE
                        and self.policy.node.resource.reference_type
                        == ReferenceType.STATIC
                    ):
                        try:
                            prop = getResourceProp(
                                var,
                                self.policy.node.object_type,
                                self.policy.node.resource.reference_name,
                            )
                            disjoint_set.add_predicate(
                                PolicyPredicate(f"eq({var}, '{prop}')")
                            )
                            continue
                        except Exception as e:
                            logger.debug(f"Error while resolving {prop} offline: {e}")

                    disjoint_set.add_predicate(
                        PolicyPredicate(
                            f"eq({var}, '{{getResourceProp('{var}', '{self.policy.node.object_type}', '{self.policy.node.resource.reference_name}')}}')"
                        )
                    )
                elif var.startswith("Object"):
                    raise NotImplementedError("Object variables not supported yet")
                else:
                    pass

            # Resolve special growlithe predicates
            for predicate in disjoint_set.predicates.copy():
                if predicate.predicate_name == "taintSetIncludes":
                    # TODO: Add offline optimizations for taint checks
                    # TODO: Replace helper function with prop within node for taint labels
                    disjoint_set.add_predicate(
                        PolicyPredicate(
                            f"eq({predicate.arguments[0]}, '{online_taint_label(self.policy.node)}')"
                        )
                    )

    @property
    def deferred_query(self) -> str:
        return " & ".join(
            [
                f"{disj.deferred_query}"
                for disj in self.disjoint_predicates
                if disj.deferred_query is not None
            ]
        )

    @property
    def query(self) -> str:
        return " & ".join([f"({disj.query})" for disj in self.disjoint_predicates])


class Policy:
    def __init__(self, policy_type: str, policy_str: str, node: Node = None):
        self.node = node
        self.policy_type = policy_type
        self.policy_str = "" if policy_str == "allow" else policy_str
        self.policy_clauses: List[PolicyClause] = self.parse_policy_str(self.policy_str)

    def __str__(self) -> str:
        return "allow" if self.policy_str == "" else self.policy_str

    def parse_policy_str(self, policy_str: str) -> List[PolicyClause]:
        if policy_str == "":
            return []

        # Function to process a single clause
        def process_clause(clause_str: str) -> PolicyClause:
            # Remove outer parentheses if present
            clause_str = clause_str.strip()
            if clause_str.startswith("(") and clause_str.endswith(")"):
                clause_str = clause_str[1:-1].strip()

            # Split the clause into predicates (separated by '&')
            predicate_strs = re.split(r"\s*&\s*", clause_str)
            predicates = [PolicyPredicate(pred.strip()) for pred in predicate_strs]
            return PolicyClause(predicates, self)

        # Normalize whitespace, including newlines
        policy_str = re.sub(r"\s+", " ", policy_str.strip())

        # Check if the policy has multiple clauses
        if re.search(r"\s+or\s+", policy_str, re.IGNORECASE):
            # Split the policy string into clauses (separated by 'or')
            clause_strs = re.split(r"\s+or\s+", policy_str, flags=re.IGNORECASE)
            return [process_clause(clause) for clause in clause_strs]
        else:
            # Single clause policy
            return [process_clause(policy_str)]

    def generate_assertion(self, language) -> str:
        if language == "python":
            return self.generate_python_assertion()

    def generate_python_assertion(self) -> str:
        # Generate the pyDatalog assertion string for python
        valid_queries = []

        for clause in self.policy_clauses:
            query = clause.deferred_query if HYBRID_ENFORCEMENT_MODE else clause.query
            if query != "":
                valid_queries.append(f'pyDatalog.ask(f"{query}") != None')

        if not valid_queries:
            return ""
        else:
            return (
                f"assert {' or '.join(valid_queries)}, 'Policy evaluated to be false'"
            )
