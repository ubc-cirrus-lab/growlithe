import re
from src.logger import logger
from src.graph.graph import *


def create_node_from_side(side, related_locations, default_function="UNKNOWN"):
    if "None" in side:
        logger.warning("Side is None")
        # Create a default node with a specific identifier
        default_node = Node(
            Reference(ReferenceType.STATIC, "DefaultNode"),
            "DEFAULT_TYPE",
            Reference(ReferenceType.STATIC, "DefaultDataObject"),
            Scope.INVOCATION,
            InterfaceType.SOURCE,
            default_function,
            attributes={},
        )
        return default_node, None

    match = re.match(
        r"\[([^,]+),\s([^,]+),\s([^:]+):([^:]+):([^,]+),\s([^:]+):([^:]+)\]\((\d+)\)",
        side,
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

        node = Node(
            Reference(reference_type, reference_name),
            resource_type,
            Reference(data_object_reference_type, data_object_reference_name),
            scope,
            interface_type,
            default_function,
            attributes={},
        )

        # Add properties
        node.attributes["properties"] = groups[7]
        return node, related_locations[int(groups[7]) - 1]
    else:
        logger.error(f"Invalid format in side: {side}")
        return None, None


def parse_and_add_flow(flow, graph, related_locations, default_function="UNKNOWN"):
    sides = flow.split("==>")

    if len(sides) == 2:
        source_side, sink_side = sides

        # Parse source side
        source_node, source_location = create_node_from_side(
            source_side, related_locations, default_function
        )

        # Parse sink side
        sink_node, sink_location = create_node_from_side(
            sink_side, related_locations, default_function
        )

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
