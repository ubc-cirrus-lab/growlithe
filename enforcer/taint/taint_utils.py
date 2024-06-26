
"""
Offline taint label is the most conservative taint associated with the node offline.
The offline taint labels would use ? if a resource/object name is dynamic, else will use the associated immutable string
"""

from graph.adg.node import Node
from graph.adg.types import ReferenceType, TaintLabelMatch


def offline_taint_label(node: Node):
    if node.resource.reference_type == ReferenceType.DYNAMIC:
        r = "?"
    else:
        r = node.resource.reference_name

    if node.object.reference_type == ReferenceType.DYNAMIC:
        o = "?"
    else:
        o = node.object.reference_name
    return f"node_id:{r}:{o}"

"""Generates taint labels to be used when instrumenting source code.
The formatted string is generated offline, but when used at runtime gives the online taint label
"""
def online_taint_label(node: Node):
    if node.resource.reference_type == ReferenceType.DYNAMIC:
        r = "{" + node.resource.reference_name + "}"
    else:
        r = node.resource.reference_name

    if node.object.reference_type == ReferenceType.DYNAMIC:
        o = "{" + node.object.reference_name + "}"
    else:
        o = node.object.reference_name
    return f"{node.node_id}:{r}:{o}"

# //Returns Match, PossibleMatch (at runtime) and NoMatch
def offline_match(node: Node, node2: Node):
    parts1 = node.offline_taint_label().split(':')
    parts2 = node2.offline_taint_label().split(':')
    
    def match_part(part1, part2):
        if part1 == '*' or part2 == '*':
            return TaintLabelMatch.MATCH
        elif part1 == '?' or part2 == '?':
            return TaintLabelMatch.POSSIBLE_MATCH
        else:
            return TaintLabelMatch.MATCH if part1 == part2 else TaintLabelMatch.NO_MATCH
    
    results = [match_part(parts1[i], parts2[i]) for i in range(len(parts1))]

    if TaintLabelMatch.NO_MATCH in results:
        return TaintLabelMatch.NO_MATCH
    elif TaintLabelMatch.POSSIBLE_MATCH in results:
        return TaintLabelMatch.POSSIBLE_MATCH
    else:
        return TaintLabelMatch.MATCH
