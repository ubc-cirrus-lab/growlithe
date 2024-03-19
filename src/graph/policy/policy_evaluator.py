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
    if ' or ' in policy_str:
        clauses = policy_str.split(' or ')
    else:
        clauses = [policy_str]

    assertions = []
    for clause in clauses:
        dynamic_eval = False            
        if 'taintSetContains' in clause:
            dynamic_eval = True
            pattern = r"taintSetContains\('([^']+)'\)"
            def repl(m):
                argument = m.group(1)  # Get the captured argument
                return f"taintSetContains('{node.id}', '{argument}')"
            clause = re.sub(pattern, repl, clause)

        # Replace DataConduit Variables
        required_meta_props = re.findall(r'\bMeta\w+', clause)
        if required_meta_props:
            for prop in required_meta_props:
                if node.resource_name.reference_type == ReferenceType.DYNAMIC:
                    dynamic_eval = True
                    clause = f"({prop}=='{{getMetaProp('{prop}', '{node.resource_type}', {node.resource_name.reference_name})}}') & " + clause
            logger.info(required_meta_props)
            logger.info(clause)

        required_props = re.findall(r'\bProp\w+', clause)
        for prop in required_props:
            if prop in node.attributes:
                if node.attributes[prop].reference_type == ReferenceType.DYNAMIC:
                    dynamic_eval = True
                    clause = f"({prop}=='{{{node.attributes[prop].reference_name}}}') & " + clause
                else:
                    clause = clause.replace(prop, f'"{node.attributes[prop].reference_name}"')

        
        # Replace Session Variables
        required_session_props = set(re.findall(r'\bSession\w+', clause))
        if required_session_props:
            dynamic_eval = True
            # Generate inline assertion
            for prop in required_session_props:
                clause = f"({prop}=='{{getSessionProp('{prop}')}}') & " + clause

            # Simulate runtime check
            # print(pyDatalog.ask(policy_rhs))
            # assert pyDatalog.ask(clause) != None, 'Simulated Policy evaluated to be false'

        if not dynamic_eval:
            if pyDatalog.ask(clause) == None:
                logger.warn(f"==POLICY CLAUSE FAILED STATICALLY==: {clause}")
                return False
            else:
                logger.info(f"Static eval pass: {clause}")
            return True
        assertions.append(clause)
    
    # Tranform assertions to pyDatalog.ask() format
    assertions = [f"pyDatalog.ask(f\"{clause}\") != None" for clause in assertions]
    # Get assert pyDatalog.ask(c1)!=None or pyDatalog.ask(c2)!=None or ... , "Policy evaluated to be false"
    return f"assert {' or '.join(assertions)}, 'Policy evaluated to be false'"
    