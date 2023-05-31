import networkx as nx
import matplotlib.pyplot as plt
from node import Node, Node_Type, Security_Type, Endpoint_Type
import utility
import json

class Graph:
    def __init__(self):
        self.nodes = []

    def find_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None
    
    def find_node_by_physicalLocation(self, physicalLocation):
        for node in self.nodes:
            if node != None and node.physicalLocation == physicalLocation:
                return node
        return None

    def find_node_or_create(self, name, physicalLocation=None):
        if physicalLocation is not None:
            node = self.find_node_by_physicalLocation(physicalLocation)
        else:
            node = self.find_node(name)
        if node is None:
            node = Node(name)
            self.nodes.append(node)
        return node

    # Returns the node with the given endpoint type, returns first node if multiple nodes have the given endpoint type
    def find_internal_node_by_endpoint_type(self, function_node, endpoint_type):
        for node in function_node.internal:
            if node.endpoint_type == endpoint_type:
                return node
        return None

    def init_security_labels(self, security_labels_file):
        privateLocations = json.load(open(security_labels_file))["private"]
        for location in privateLocations:
            node = self.find_node_by_physicalLocation(location)
            if node is not None:
                node.security_type = Security_Type.PRIVATE
            else:
                print(f"Warning: {location} not found in graph")
    
    def traverse_propagate_labels(self):
        # Internal propagation
        for node in self.nodes:
            if node.parent_function is None:
                for internal in node.internal:
                    self.propagate_labels(internal)

    # Traverse the graph and propagate private labels
    def propagate_labels(self, node):
        if node.security_type == Security_Type.PUBLIC:
            return
        for child in node.children:
            child.security_type = Security_Type.PRIVATE
            self.propagate_labels(child)

    def connect_nodes_across_functions(self, function_node):
        for next_node in function_node.children:
            node1 = self.find_internal_node_by_endpoint_type(function_node, Endpoint_Type.RETURN)
            # FIXME: There can be multiple params in next_node
            node2 = self.find_internal_node_by_endpoint_type(next_node, Endpoint_Type.PARAM)
            if node1 is not None and node2 is not None:
                node1.add_child(node2)
            self.connect_nodes_across_functions(next_node)

    @property
    def root(self):
        return self.nodes[0]
    
    def print(self):
        utility.print_line()
        for node in self.nodes:
            print(f"{node.name : <10}\
                  (Parent: {node.parent_function.name if node.parent_function else 'None'})\
                  (Children: {[child.name for child in node.children]})\
                  (Internal: {[internal.name for internal in node.internal]})\)")

    def visualize(self, vis_out_path, graphic=False):
        if graphic:
            nodes = [node.name for node in self.nodes if node.parent_function is None]
            nodes.append("End")

            G = nx.DiGraph()
            G.add_nodes_from(nodes)

            self.add_edges(G)

            node_sizes, node_colors = self.customize_nodes()

            edge_styles = {edge: G.edges[edge]["style"] for edge in G.edges}

            pos = nx.spring_layout(G, seed=5)
            nx.draw_networkx(
                G,
                pos=pos,
                with_labels=True,
                arrows=True,
                node_size=[node_sizes[n] for n in nodes],
                node_color=[node_colors[n] for n in nodes],
                style=[edge_styles[edge] for edge in G.edges],
            )

            legend_handles = self.customize_legends()
            plt.legend(handles=legend_handles, loc="lower right")
            plt.show(block=False)
            plt.savefig(vis_out_path, format="PNG")
        else:
            for node in self.nodes:
                if node.children == []:
                    print(
                        f"{node.name} ({node.parent_function.name if node.parent_function else 'None'}) -> End"
                    )
                for child in node.children:
                    print(
                        f"{node.name} ({node.parent_function.name if node.parent_function else 'None'}) -> {child.name}"
                    )

    def customize_legends(self):
        legend_handles = []
        legend_handles.append(
                plt.Line2D(
                    [],
                    [],
                    color="blue",
                    marker="o",
                    linestyle="None",
                    markersize=10,
                    label="resource",
                )
            )
        legend_handles.append(
                plt.Line2D(
                    [],
                    [],
                    color="green",
                    marker="o",
                    linestyle="None",
                    markersize=10,
                    label="function",
                )
            )
        legend_handles.append(
                plt.Line2D(
                    [],
                    [],
                    color="red",
                    marker="o",
                    linestyle="None",
                    markersize=10,
                    label="end",
                )
            )

        legend_handles.append(
                plt.Line2D(
                    [], [], color="black", linestyle="solid", label="Function edge"
                )
            )
        legend_handles.append(
                plt.Line2D(
                    [], [], color="black", linestyle="dashed", label="Resource edge"
                )
            )
        
        return legend_handles

    def customize_nodes(self):
        node_sizes = {}
        node_colors = {}
        for node in self.nodes:
            if node.type == Node_Type.RESOURCE:
                node_sizes[node.name] = 500
                node_colors[node.name] = "blue"
            else:
                node_sizes[node.name] = 1000
                node_colors[node.name] = "green"
        node_sizes["End"] = 1000
        node_colors["End"] = "red"
        return node_sizes, node_colors

    def add_edges(self, G):
        for node in self.nodes:
            if node.parent_function is not None:
                name = node.parent_function.name
            else:
                name = node.name
            if node.children == []:
                G.add_edge(name, "End", style="solid")
            for child in node.children:
                if child.type == Node_Type.RESOURCE or node.type == Node_Type.RESOURCE:
                    style = "dashed"
                else:
                    style = "solid"
                if child.parent_function is not None:
                    G.add_edge(name, child.parent_function.name, style=style)
                else:
                    G.add_edge(name, child.name, style=style)
