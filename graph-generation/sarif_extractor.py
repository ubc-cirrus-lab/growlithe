import re
import utility
from node import DataflowType, NodeType

def add_internal_nodes(sarif_file_path, function_node, graph, dataflowType):
    results = utility.get_query_results(sarif_file_path)
    if len(results) <= 0:
        print("No results found in SARIF file")

    for result in results:
        # print("Parsing result: ", result["message"]["text"])
        # action_pattern = r"\[(\w+)\]\((\d+)\)"
        action_pattern = r"\[(\w+:\w+)\]\((\d+)\)"
        match = re.search(action_pattern, result["message"]["text"])
        if match:
            name, type = match.group(1).split(":")
            physicalLocation = result["locations"][int(match.group(2)) - 1]["physicalLocation"]
            node = graph.find_node_or_create(name, physicalLocation)

            node.nodeType = NodeType[type]
            node.physicalLocation = physicalLocation
            node.dataflowType = dataflowType
            node.parentFunctionNode = function_node
            if not node.is_root_node():
                outerNode = graph.find_node_or_create(f"{type}/{name}")
                outerNode.nodeType = node.nodeType
                if dataflowType == DataflowType.SOURCE:
                    outerNode.add_edge(node)
                elif dataflowType == DataflowType.SINK:
                    node.add_edge(outerNode)
            function_node.add_child(node)

def add_internal_edges(sarif_file_path, graph):
    results = utility.get_query_results(sarif_file_path)
    if len(results) <= 0:
        print("No results found in SARIF file")
    for result in results:
        for codeFlow in result["codeFlows"]:
            srcLocation = codeFlow["threadFlows"][0]["locations"][0]["location"]["physicalLocation"]
            dstLocation = codeFlow["threadFlows"][0]["locations"][-1]["location"]["physicalLocation"]
            src_node = graph.find_node_by_physicalLocation(srcLocation)
            dst_node = graph.find_node_by_physicalLocation(dstLocation)
            if src_node is None or dst_node is None:
                print("Source or destination node not found")
            src_node.add_edge(dst_node)
            print("Adding edge from ", src_node.name, " to ", dst_node.name)