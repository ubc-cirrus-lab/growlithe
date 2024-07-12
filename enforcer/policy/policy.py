import re
from typing import List, Set


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
            print(f"Error: '{self.predicate_str}' is not a valid function predicate")
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
    
    def evaluate(self):
        pass


class PolicyClause:
    """OR separated policy clause in a DNF policy"""

    def __init__(self, predicates: List[PolicyPredicate]):
        self.predicates: List[PolicyPredicate] = predicates
        self.disjoint_predicates: List[PredicateSet] = self.divide_into_disjoint_sets()
        self.insert_implicit_predicate()

    # # Each clause can have set of predicates that can be evaluated independently of the other predicates
    def divide_into_disjoint_sets(self) -> List[PredicateSet]:
        disjoint_sets: List[PredicateSet] = []
        predicates = self.predicates.copy()
        while predicates:
            predicate = predicates.pop(0)
            current_set = set({predicate})
            current_vars = predicate.variables
            i = 0
            while i < len(predicates):
                if current_vars & predicates[i].variables:
                    current_set.append(predicates.pop(i))
                    current_vars.update(current_set[-1].variables)
                else:
                    i += 1
            disjoint_sets.append(PredicateSet(current_set))
        return disjoint_sets

    def insert_implicit_predicate(self):
        for disjoint_set in self.disjoint_predicates:
            # TODO: Replace with properties stored in node/edge objects
            for var in disjoint_set.variables:
                if var.startswith("Session"):
                    print(f"Adding implicit predicate for session variable: {var}")
                    disjoint_set.add_predicate(
                        PolicyPredicate(f"eq({var}, '{{getSessionVar('{var}')}}')")
                    )
                elif var.startswith("Inst"):
                    raise NotImplementedError("Instance variables not supported yet")
                elif var.startswith("Object"):
                    raise NotImplementedError("Object variables not supported yet")
                else:
                    pass

    @property
    def query(self) -> str:
        return " & ".join(
            [
                f"{pred.predicate_str}"
                for disj in self.disjoint_predicates
                for pred in disj.predicates
            ]
        )


class Policy:
    def __init__(self, policy_type: str, policy_str: str):
        self.policy_type = policy_type
        self.policy_str = policy_str
        self.policy_clauses: List[PolicyClause] = self.parse_policy_str(policy_str)

    def parse_policy_str(self, policy_str: str) -> List[PolicyClause]:
        # Split the policy string into clauses (separated by 'or')
        clause_strs = re.split(r"\s+or\s+", policy_str.strip())

        clauses: List[PolicyClause] = []
        for clause_str in clause_strs:
            # Remove outer parentheses
            clause_str = clause_str.strip()[1:-1]

            # Split the clause into predicates (separated by '&')
            predicate_strs = re.split(r"\s*&\s*", clause_str)

            predicates: List[PolicyPredicate] = [
                PolicyPredicate(pred) for pred in predicate_strs
            ]
            clauses.append(PolicyClause(predicates))
        return clauses

    def generate_assertion(self, language) -> str:
        if language == "python":
            return self.generate_python_assertion()

    def generate_python_assertion(self) -> str:
        # Generate the pyDatalog assertion string for python

        pyDatalog_queries = [
            f'pyDatalog.ask(f"{clause.query}") != None'
            for clause in self.policy_clauses
        ]
        # Get the python statement: assert pyDatalog.ask(c1)!=None or pyDatalog.ask(c2)!=None or ... , "Policy evaluated to be false"
        return (
            f"assert {' or '.join(pyDatalog_queries)}, 'Policy evaluated to be false'"
        )
