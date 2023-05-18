import re
from node import Node_Type


# extend the high-level graph with the boto3 coarse-grained query results
def extend_graph(result, function_node, graph):
    for line in result["message"]["text"].split("\n"):
        action_pattern = r"from \[(\w+)\]\((\d+)\) ==> \[(\w+)\]\((\d+)\)"
        match = re.search(action_pattern, line)
        if match:
            node = graph.find_node_or_create(match.group(1))
            node.type = Node_Type.RESOURCE
            if match.group(1) == "event":
                node.parent_function = graph.find_node_or_create(function_node.name)
            child = graph.find_node_or_create(match.group(3))
            child.type = Node_Type.RESOURCE
            node.add_child(child)
