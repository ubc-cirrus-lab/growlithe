import re
import utility
from node import Node_Type

def add_internal_nodes(sarif_file_path, function_node, graph, node_type):
    results = utility.get_query_results(sarif_file_path)
    if len(results) <= 0:
        # TODO: Add fix for 0 results
        SystemError("No results found in SARIF file")

    for result in results:
        print("Parsing result: ", result["message"]["text"])
        # action_pattern = r"\[(\w+)\]\((\d+)\)"
        action_pattern = r"\[(\w+:\w+)\]\((\d+)\)"
        match = re.search(action_pattern, result["message"]["text"])
        if match:
            name, endpoint_type = match.group(1).split(":")
            physicalLocation = result["locations"][int(match.group(2)) - 1]["physicalLocation"]
            node = graph.find_node_or_create(name, physicalLocation)
            node.endpoint_type = endpoint_type
            node.physicalLocation = physicalLocation
            node.type = node_type
            node.parent_function = function_node
            function_node.internal.append(node)

def add_internal_edges(sarif_file_path, graph):
    results = utility.get_query_results(sarif_file_path)
    if len(results) <= 0:
        SystemError("No results found in SARIF file")
    for result in results:
        srcLocation = result["codeFlows"][0]["threadFlows"][0]["locations"][0]["location"]["physicalLocation"]
        dstLocation = result["codeFlows"][0]["threadFlows"][0]["locations"][-1]["location"]["physicalLocation"]
        src_node = graph.find_node_by_physicalLocation(srcLocation)
        dst_node = graph.find_node_by_physicalLocation(dstLocation)
        if src_node is None or dst_node is None:
            SystemError("Source or destination node not found")
        src_node.add_child(dst_node)
