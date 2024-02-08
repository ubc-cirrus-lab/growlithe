import re
from src.graph.policy.policy_predicates import *
from src.logger import logger
from src.graph.graph import ReferenceType

# Tries to evaluate a policy using pyDatalog
# Returns:
    # False if the policy evaluation fails statically
    # True if the policy evaluation passes statically
    # Assertion string if the policy evaluation requires runtime checks
def try_policy_eval(policy_str, node):
    if policy_str == 'allow':
        return True
    dynamic_eval = False

    if 'taintSetContains' in policy_str:
        dynamic_eval = True
        pattern = r"taintSetContains\('([^']+)'\)"
        def repl(m):
            argument = m.group(1)  # Get the captured argument
            return f"taintSetContains('{node.id}', '{argument}')"
        policy_str = re.sub(pattern, repl, policy_str)


    # Replace DataConduit Variables
    required_props = re.findall(r'\bProp\w+', policy_str)
    for prop in required_props:
        if prop in node.attributes:
            if node.attributes[prop].reference_type == ReferenceType.DYNAMIC:
                dynamic_eval = True
                policy_str = f"({prop}=='{{{node.attributes[prop].reference_name}}}') & " + policy_str
            else:
                policy_str = policy_str.replace(prop, f'"{node.attributes[prop].reference_name}"')
            # TODO: Handle case of dynamic properties

    
    # Replace Session Variables
    required_session_props = set(re.findall(r'\bSession\w+', policy_str))
    if required_session_props:
        dynamic_eval = True
        # Generate inline assertion
        for prop in required_session_props:
            policy_str = f"({prop}=={{getSessionProp('{prop}')}}) & " + policy_str

        # Simulate runtime check
        # print(pyDatalog.ask(policy_rhs))
        # assert pyDatalog.ask(policy_str) != None, 'Simulated Policy evaluated to be false'

    if not dynamic_eval:
        # logger.info(f"Evaluation Result {pyDatalog.ask(policy_str)}")
        if pyDatalog.ask(policy_str) == None:
            logger.warn(f"Policy cannot be satisfied {policy_str}")
            return False
        else:
            logger.info(f"Static eval pass: {policy_str}")
        return True

    return f"assert pyDatalog.ask(f\"{policy_str}\") != None, 'Policy evaluated to be false'"
    