import re

from src import utility
from src.logger import logger
from src.graph.node import DataflowType, NodeType


def add_internal_nodes(sarif_file_path, function_node, graph, dataflow_type):
    results = utility.get_query_results(sarif_file_path)
    if len(results) <= 0:
        logger.info("No results found in SARIF file")

    for result in results:
        action_pattern = r"\[(\w+:\w+)\]\((\d+)\)"
        match = re.search(action_pattern, result["message"]["text"])
        if match:
            name, type = match.group(1).split(":")
            physical_location = result["locations"][int(match.group(2)) - 1]["physicalLocation"]
            node = graph.find_node_or_create(name, physical_location)

            node.node_type = NodeType[type]
            node.physical_location = physical_location
            node.dataflow_type = dataflow_type
            node.parent_function_node = function_node
            if not node.is_root_node():
                outer_node = graph.find_node_or_create(f"{type}/{name}")
                outer_node.node_type = node.node_type
                if dataflow_type == DataflowType.SOURCE:
                    outer_node.add_edge(node)
                elif dataflow_type == DataflowType.SINK:
                    node.add_edge(outer_node)
            function_node.add_child(node)


def add_internal_edges(sarif_file_path, graph):
    results = utility.get_query_results(sarif_file_path)
    if len(results) <= 0:
        logger.info("No results found in SARIF file")

    for result in results:
        for codeFlow in result["codeFlows"]:
            src_location = codeFlow["threadFlows"][0]["locations"][0]["location"]["physicalLocation"]
            dst_location = codeFlow["threadFlows"][0]["locations"][-1]["location"]["physicalLocation"]
            src_node = graph.find_node_by_physical_location(src_location)
            dst_node = graph.find_node_by_physical_location(dst_location)
            if src_node is None or dst_node is None:
                logger.info("Source or destination node not found")
            src_node.add_edge(dst_node)
            logger.info("Adding edge from ", src_node.name, " to ", dst_node.name)


def add_node_conditions(sarif_file_path, graph, app_src_path):
    results = utility.get_query_results(sarif_file_path)
    if len(results) <= 0:
        logger.info("No results found in SARIF file")

    for result in results:
        action_pattern = r"\[(\w+:\w+)\]\((\d+)\) requires (\w+) for \[condition\]\((\d+)\)"
        match = re.search(action_pattern, result["message"]["text"])
        physical_location = result["locations"][int(match.group(2)) - 1]["physicalLocation"]
        node = graph.find_node_by_physical_location(physical_location)
        conditional_boolean = bool(match.group(3))
        condition = result["relatedLocations"][int(match.group(4)) - 1]
        node.conditions.add((conditional_boolean, utility.get_string_from_location(condition, app_src_path)))
