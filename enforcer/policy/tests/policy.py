from enforcer.policy.policy import Policy
from enforcer.policy.growlithe import *
from graph.adg.function import Function
from graph.adg.node import Node
from graph.adg.types import Reference, ReferenceType, Scope

# Example usage

policy_str = """
    (   eq(1, 1) &
        eq(Resource, 'resource') &
        eq(InstRegion, ResourceRegion)    ) or 
    (
        eq(Resource, 'resource') &
        eq(InstRegion, ResourceRegion)
    ) or (
        eq(Resource, 'Other-resource')
    )
"""

test_node = Node(
    Reference(ReferenceType.STATIC, "resource"),
    Reference(ReferenceType.STATIC, "object"),
    "object_type",
    "object_handler",
    "object_code_location",
    Function("object_fn", None, None, None),
    {"object_attr": "object_attr"},
    {"resource_attr": "resource_attr"},
    Scope.GLOBAL,
)


def test_policy_parsing():
    policy = Policy("WRITE", policy_str, test_node)
    # Print the parsed policy
    for i, clause in enumerate(policy.policy_clauses):
        print(f"Clause {i + 1}:")
        for j, predicate in enumerate(clause.predicates):
            print(
                f"  Predicate {j + 1}: {predicate.predicate_str} with variables {predicate.variables}"
            )
        print()
    assert len(policy.policy_clauses) == 3
    assert len(policy.policy_clauses[0].predicates) == 3
    assert len(policy.policy_clauses[1].predicates) == 2
    assert len(policy.policy_clauses[2].predicates) == 1

    print("Generated assertion")
    assertion = policy.generate_assertion("python")
    print(assertion)
    # assert assertion == """assert pyDatalog.ask(f"eq(InstRegion, '{getInstProp('InstRegion')}') & eq(ResourceRegion, 'None') & eq(InstRegion, ResourceRegion)") != None or pyDatalog.ask(f"eq(InstRegion, ResourceRegion) & eq(InstRegion, '{getInstProp('InstRegion')}') & eq(ResourceRegion, 'None')") != None, 'Policy evaluated to be false'"""
    print()


test_policy_parsing()


def test_disjoint_sets():
    policy = Policy("WRITE", policy_str, test_node)
    # Print the parsed policy and disjoint sets
    for i, clause in enumerate(policy.policy_clauses):
        print(f"Clause {i + 1}:")
        disjoint_sets = clause.disjoint_predicates
        for j, disjoint_set in enumerate(disjoint_sets):
            print(f"  Disjoint Set {j + 1}:")
            for predicate in disjoint_set.predicates:
                print(f"    Predicate: {predicate.predicate_str}")
        print()
    assert len(policy.policy_clauses[0].disjoint_predicates[0].predicates) == 1
    assert len(policy.policy_clauses[0].disjoint_predicates[1].predicates) == 2
    assert len(policy.policy_clauses[0].disjoint_predicates[2].predicates) == 3
    assert len(policy.policy_clauses[1].disjoint_predicates[0].predicates) == 2
    assert len(policy.policy_clauses[1].disjoint_predicates[1].predicates) == 3
    assert len(policy.policy_clauses[2].disjoint_predicates[0].predicates) == 2

test_disjoint_sets()
