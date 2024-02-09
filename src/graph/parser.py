import re
from src.logger import logger
from src.graph.graph import *


# Returns a node and its related location to use in edge
def create_node_from_side(node_str, related_locations, function="UNKNOWN"):
    if "None" in node_str:
        logger.warning("Side is None. Creating a default node")
        # Create a default node with a specific identifier
        # TODO: Can make a helper function for a "default node" to represent
        default_node = DefaultNode(function)
        return default_node, None

    match = re.match(
        r"\[([^,]+),\s([^,]+),\s([^:]+):([^:]+):([^,]+),\s([^:]+):([^:]+)\]\((\d+)\)",
        node_str,
    )
    if match:
        groups = match.groups()
        interface_type = InterfaceType[groups[0]]
        scope = Scope[groups[1]]
        resource_type = groups[2]
        reference_type = ReferenceType[groups[3]]
        reference_name = groups[4]
        data_object_reference_type = ReferenceType[groups[5]]
        data_object_reference_name = groups[6]

        code_path = related_locations[int(groups[7]) - 1]
        node = Node(
            Reference(reference_type, reference_name),
            resource_type,
            Reference(data_object_reference_type, data_object_reference_name),
            scope,
            interface_type,
            function,
            attributes={},
        )
        return node, code_path
    else:
        logger.error(f"Invalid format in side: {node_str}")
        return None, None


def parse_and_add_flow(
    flow, graph: Graph, related_locations, default_function="UNKNOWN"
):
    if default_function != "UNKNOWN":
        graph.add_function(default_function)

    flow_ends = flow.split("==>")

    if len(flow_ends) == 2:
        source_side, sink_side = flow_ends

        # Parse source side
        source_node, source_location = create_node_from_side(
            source_side, related_locations, default_function
        )

        # Parse sink side
        sink_node, sink_location = create_node_from_side(
            sink_side, related_locations, default_function
        )

        # This will reuse same default node to prevent isolated nodes
        # TODO: Check if we need to create a new node for each default node
        if source_node and sink_node and source_node != sink_node:
            # Get or add source node to the graph
            source_node = graph.get_existing_or_add_node(source_node)

            # Get or add sink node to the graph
            sink_node = graph.get_existing_or_add_node(sink_node)

            # Create edge
            edge = Edge(
                source_node,
                sink_node,
                {"CodePath": source_location},
                {"CodePath": sink_location},
            )
            graph.add_edge(edge)
    else:
        logger.error(f"Invalid flow format: {flow}")
