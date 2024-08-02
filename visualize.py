import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.patches as mpatches
import numpy as np

from growlithe.graph.adg.graph import Graph

def visualize(graph: Graph):
    # Create a new directed graph
    G = nx.DiGraph()

    # Add nodes and edges to the graph
    for node in graph.nodes:
        G.add_node(node.node_id, **node.to_json())
    for edge in graph.edges:
        G.add_edge(edge.source.node_id, edge.sink.node_id, edge_type=edge.edge_type)

    # Group nodes by function
    function_groups = defaultdict(list)
    for node in graph.nodes:
        function_groups[node.object_fn.name].append(node.node_id)

    # Define colors for different ObjectTypes
    color_map = {
        'S3_BUCKET': '#FFA07A',  # Light Salmon
        'LOCAL_FILE': '#98FB98',  # Pale Green
        'PARAM': '#87CEFA',  # Light Sky Blue
        'RETURN': '#DDA0DD',  # Plum
        'S3': '#F0E68C'  # Khaki
    }

    # Set up the plot
    fig, ax = plt.subplots(figsize=(24, 18))

    # Custom positioning for function groups
    num_functions = len(function_groups)
    function_positions = {}
    for i, (function, nodes) in enumerate(function_groups.items()):
        x = i / (num_functions - 1) if num_functions > 1 else 0.5
        function_positions[function] = (x, 0.5)

    # Position nodes within their function groups
    pos = {}
    for function, nodes in function_groups.items():
        base_x, base_y = function_positions[function]
        for j, node in enumerate(nodes):
            angle = 2 * np.pi * j / len(nodes)
            radius = 0.15  # Adjust this value to control group spread
            pos[node] = (base_x + radius * np.cos(angle), base_y + radius * np.sin(angle))

    # Draw function group backgrounds
    for function, (x, y) in function_positions.items():
        nodes = function_groups[function]
        node_positions = np.array([pos[node] for node in nodes])
        centroid = node_positions.mean(axis=0)
        max_distance = np.max(np.linalg.norm(node_positions - centroid, axis=1))
        circle = plt.Circle(centroid, max_distance + 0.05, fill=True, alpha=0.2, ec='gray', fc='lightgray')
        ax.add_patch(circle)
        ax.text(centroid[0], centroid[1] + max_distance + 0.07, function, fontsize=14, fontweight='bold', 
                ha='center', va='center', bbox=dict(facecolor='white', edgecolor='black', alpha=0.8))

    # Draw edges with arrows
    edge_colors = ['gray' if G.nodes[u]['ObjectType'] != 'RETURN' else 'red' for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True, arrowsize=20, width=1.5, alpha=0.6, ax=ax)

    # Draw nodes
    node_colors = [color_map.get(G.nodes[node]['ObjectType'], '#FFFFFF') for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3000, alpha=0.8, ax=ax)

    # Add node labels
    labels = {node.node_id: f"{node.node_id}\n{node.object.__str__()}\n{node.object_type}" for node in graph.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold', ax=ax)

    # Add edge labels
    edge_labels = {(edge.source.node_id, edge.sink.node_id): edge.edge_type for edge in graph.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, alpha=0.7, ax=ax)

    # Add a legend for node colors
    legend_elements = [mpatches.Patch(color=color, label=object_type) for object_type, color in color_map.items()]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)

    # Adjust the layout and display the plot
    ax.set_title("Graph Visualization", fontsize=16, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    plt.show()