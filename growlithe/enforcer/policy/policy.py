from __future__ import annotations
import re
from typing import List, Set
from growlithe.common.logger import logger
from growlithe.common.tasks_config import HYBRID_ENFORCEMENT_MODE
from pyDatalog import pyDatalog
from growlithe.enforcer.taint.taint_utils import online_taint_label, offline_match
from growlithe.graph.adg.node import Node
from growlithe.graph.adg.types import ReferenceType
from growlithe.config import get_config

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

    @property
    def contains_taint_predicates(self) -> bool:
        return any(pred.predicate_name.startswith("taint") for pred in self.predicates)

    @property
    def taint_predicates(self) -> Set[PolicyPredicate]:
        taint_preds = set()
        for pred in self.predicates:
            if pred.predicate_name.startswith("taint"):
                taint_preds.add(pred)
        return taint_preds

    def add_predicate(self, predicate: PolicyPredicate):
        self.predicates.add(predicate)

    def remove_predicate(self, predicate: PolicyPredicate):
        self.predicates.remove(predicate)

    @property
    def query(self) -> str:
        return " & ".join([f"{pred.predicate_str}" for pred in self.predicates])

    def deferred_query(self, node: Node) -> str:
        logger.debug(f"Checking offline for {self.query}")
        taint_predicates = self.taint_predicates
        if len(taint_predicates) != 0:
            for taint_pred in taint_predicates:
                if taint_pred.predicate_name == "taintSetIncludes":
                    # If no possible matches for arg2 exist for ancestors of node in arg1,
                    # generate error, else defer
                    possible_match = False
                    for ancestor in node.ancestor_nodes.union(node.ancestor_functions):
                        if offline_match(taint_pred.arguments[1], ancestor):
                            possible_match = True
                    if not possible_match:
                        logger.error(f"OFFLINE POLICY ERROR: Partial policy failed offline check: {taint_pred.predicate_str}, but no upstream path can satisfy this")
                elif taint_pred.predicate_name == "taintSetExcludes":
                    # If no possible matches for arg2 exist for ancestors of node in arg1,\
                    # mark this pred as successfull and do not defer, else defer
                    possible_match = False
                    for ancestor in node.ancestor_nodes.union(node.ancestor_functions):
                        if offline_match(taint_pred.arguments[1], ancestor):
                            possible_match = True
                    if not possible_match:
                        logger.info(f"OFFLINE POLICY Optimized: No upstream path can satisfy this, removing predicate: {taint_pred.predicate_str}")
                        self.remove_predicate(taint_pred)

        if self.contains_session_variables:
            if get_config().cloud_provider == 'GCP':
                logger.warning('Not implemented')
                pass
            elif get_config().cloud_provider == 'AWS':
                return self.query
        if self.contains_taint_predicates:
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
        config = get_config()
        self.insert_implicit_predicate(config.cloud_provider)

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

    def insert_implicit_predicate(self, cloud_provider='AWS'):
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
                            if cloud_provider == "AWS":
                                from growlithe.enforcer.policy.template.growlithe import getResourceProp
                                prop = getResourceProp(
                                    var,
                                    self.policy.node.object_type,
                                    self.policy.node.resource.reference_name,
                                )
                            elif cloud_provider == "GCP":
                                if var == 'ResourceRegion':
                                    prop = self.policy.node.mapped_resource.deployed_region
                                    logger.info(f"Resolved {var} to {prop}")
                                else:
                                    from growlithe.enforcer.policy.template.growlithe_utils_gcp import getResourceProp
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
                            logger.debug(f"Error while resolving prop offline: {e}")

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

    def deferred_query(self, node) -> str:
        return " & ".join(
            [
                f"{disj.deferred_query(node)}"
                for disj in self.disjoint_predicates
                if disj.deferred_query(node) is not None
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
        if self.policy_str != "":
            logger.info(f'Found policy: {self.policy_str}')

    def __str__(self) -> str:
        return "allow" if self.policy_str == "" else self.policy_str
    def __repr__(self) -> str:
        return self.__str__()

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
        if "python" in language:
            return self.generate_python_assertion()

    def generate_python_assertion(self) -> str:
        # Generate the pyDatalog assertion string for python
        valid_queries = []
        logger.info(f"Policy: {self.policy_str}")
        for clause in self.policy_clauses:
            if HYBRID_ENFORCEMENT_MODE:
                query = clause.deferred_query(self.node)
            else:
                query = clause.query
            if query != "":
                valid_queries.append(f'pyDatalog.ask(f"{query}") != None')

        if not valid_queries:
            return ""
        else:
            return (
                f"assert {' or '.join(valid_queries)}, 'Policy evaluated to be false'"
            )
